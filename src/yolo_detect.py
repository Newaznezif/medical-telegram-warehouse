"""
YOLOv8 Image Detection Module
Loads images from data/raw/images and detects objects using YOLOv8
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import argparse
from dataclasses import dataclass
import cv2
from ultralytics import YOLO

# Import YOUR config (not settings)
from src.common.config import config
from src.common.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class DetectionResult:
    """Data class for storing detection results"""
    image_path: str
    image_name: str
    channel_name: str
    date_str: str
    detected_class: str
    confidence: float
    x_center: float
    y_center: float
    box_width: float
    box_height: float
    original_width: int
    original_height: int
    processed_at: datetime

class YOLODetector:
    """
    Production-grade YOLO detector for medical/cosmetic product images
    Loads images from data/raw/images and processes them in batches
    """
    
    # Custom classes relevant to medical/cosmetic domain
    MEDICAL_CLASSES = {
        0: 'medicine',
        1: 'cosmetic', 
        2: 'bottle',
        3: 'box',
        4: 'package',
        5: 'syringe',
        6: 'pill',
        7: 'cream',
        8: 'ointment',
        9: 'medical_device'
    }
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu'):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to custom YOLO model weights. If None, uses pretrained yolov8n.pt
            device: Device to run inference on ('cuda' or 'cpu')
        """
        self.device = device
        self.model_path = model_path or 'yolov8n.pt'
        
        # Use paths from YOUR config
        raw_data_path = Path(getattr(config, 'RAW_DATA_PATH', './data/raw'))
        processed_data_path = Path(getattr(config, 'PROCESSED_DATA_PATH', './data/processed'))
        
        self.image_base_path = raw_data_path / 'images'
        self.output_dir = processed_data_path / 'detections'
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load model
        self.model = self._load_model()
        
        logger.info(f"YOLODetector initialized with model: {self.model_path}")
        logger.info(f"Image base path: {self.image_base_path}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Device: {device}")
    
    def _load_model(self) -> YOLO:
        """Load YOLO model with error handling"""
        try:
            model = YOLO(self.model_path)
            
            # Update model names with custom classes if using pretrained model
            if self.model_path == 'yolov8n.pt':
                # Map COCO classes to medical domain where possible
                coco_to_medical = {
                    39: 'bottle',      # COCO bottle -> bottle
                    67: 'cell phone',  # Could be medical device
                    73: 'book',        # Could be medical literature
                }
                for coco_id, medical_name in coco_to_medical.items():
                    if coco_id < len(model.names):
                        model.names[coco_id] = medical_name
            
            logger.info(f"Model loaded successfully with {len(model.names)} classes")
            return model
        except Exception as e:
            logger.error(f"Failed to load model from {self.model_path}: {str(e)}")
            raise
    
    def extract_channel_info(self, image_path: Path) -> Dict[str, str]:
        """
        Extract channel and date information from image path structure
        
        Expected path structure: data/raw/images/{channel_name}/{date}/{filename}
        or: data/raw/images/{channel_name}/{filename}
        
        Returns:
            Dictionary with channel_name, date_str, and filename
        """
        try:
            # Convert to list of parts
            parts = image_path.parts
            
            # Find 'images' in the path
            if 'images' in parts:
                images_idx = parts.index('images')
                channel_idx = images_idx + 1
                
                if channel_idx < len(parts):
                    channel_name = parts[channel_idx]
                    
                    # Check if next part is a date (YYYY-MM-DD format)
                    date_str = "unknown"
                    if channel_idx + 1 < len(parts):
                        next_part = parts[channel_idx + 1]
                        # Check if it looks like a date
                        if len(next_part) == 10 and next_part[4] == '-' and next_part[7] == '-':
                            try:
                                datetime.strptime(next_part, '%Y-%m-%d')
                                date_str = next_part
                            except ValueError:
                                date_str = "unknown"
                    
                    return {
                        'channel_name': channel_name,
                        'date_str': date_str,
                        'filename': parts[-1]
                    }
        except Exception as e:
            logger.warning(f"Error extracting channel info from {image_path}: {str(e)}")
        
        # Fallback: try to extract from filename or parent directory
        parent_dir = image_path.parent.name
        if parent_dir and parent_dir != 'images':
            channel_name = parent_dir
        else:
            channel_name = 'unknown'
        
        return {
            'channel_name': channel_name,
            'date_str': 'unknown',
            'filename': image_path.name
        }
    
    def get_image_dimensions(self, image_path: Path) -> Tuple[int, int]:
        """Get image dimensions without loading full image"""
        try:
            # Use OpenCV to read image dimensions efficiently
            img = cv2.imread(str(image_path))
            if img is not None:
                height, width = img.shape[:2]
                return width, height
        except Exception as e:
            logger.warning(f"Failed to get dimensions for {image_path}: {str(e)}")
        
        return 0, 0
    
    def process_single_image(self, image_path: Path, confidence_threshold: float = 0.25) -> List[DetectionResult]:
        """
        Process a single image and return detections
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence score for detections
            
        Returns:
            List of DetectionResult objects
        """
        detections = []
        
        try:
            # Check if file exists
            if not image_path.exists():
                logger.error(f"Image file not found: {image_path}")
                return detections
            
            # Get image dimensions
            width, height = self.get_image_dimensions(image_path)
            if width == 0 or height == 0:
                logger.error(f"Invalid image dimensions for {image_path}")
                return detections
            
            # Extract channel info
            channel_info = self.extract_channel_info(image_path)
            
            # Run YOLO inference
            logger.debug(f"Processing image: {image_path.name}")
            results = self.model(
                source=str(image_path),
                conf=confidence_threshold,
                iou=0.45,
                device=self.device,
                verbose=False
            )
            
            # Process results
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        # Get bounding box coordinates (normalized)
                        xywh = box.xywh.cpu().numpy()[0]
                        cls_id = int(box.cls.cpu().numpy()[0])
                        conf = float(box.conf.cpu().numpy()[0])
                        
                        # Get class name
                        class_name = result.names.get(cls_id, f"class_{cls_id}")
                        
                        # Create detection result
                        detection = DetectionResult(
                            image_path=str(image_path),
                            image_name=image_path.name,
                            channel_name=channel_info['channel_name'],
                            date_str=channel_info['date_str'],
                            detected_class=class_name,
                            confidence=conf,
                            x_center=float(xywh[0] / width),    # Normalized
                            y_center=float(xywh[1] / height),   # Normalized
                            box_width=float(xywh[2] / width),   # Normalized
                            box_height=float(xywh[3] / height), # Normalized
                            original_width=width,
                            original_height=height,
                            processed_at=datetime.now()
                        )
                        
                        detections.append(detection)
            
            logger.info(f"Processed {image_path.name}: {len(detections)} detections")
            
        except Exception as e:
            logger.error(f"Error processing {image_path}: {str(e)}", exc_info=True)
        
        return detections
    
    def find_all_images(self) -> List[Path]:
        """Find all image files in the data directory"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_paths = []
        
        for ext in image_extensions:
            image_paths.extend(self.image_base_path.rglob(f'*{ext}'))
            image_paths.extend(self.image_base_path.rglob(f'*{ext.upper()}'))
        
        # Remove duplicates and sort
        image_paths = sorted(set(image_paths))
        logger.info(f"Found {len(image_paths)} image files")
        
        return image_paths
    
    def process_batch(self, batch_size: int = 32, confidence_threshold: float = 0.25) -> pd.DataFrame:
        """
        Process all images in the data directory in batches
        
        Args:
            batch_size: Number of images to process at once
            confidence_threshold: Minimum confidence score for detections
            
        Returns:
            DataFrame containing all detections
        """
        # Find all images
        image_paths = self.find_all_images()
        
        if not image_paths:
            logger.warning("No images found to process")
            return pd.DataFrame()
        
        logger.info(f"Processing {len(image_paths)} images in batches of {batch_size}")
        
        all_detections = []
        processed_count = 0
        
        # Process in batches
        for i in range(0, len(image_paths), batch_size):
            batch = image_paths[i:i + batch_size]
            batch_number = i // batch_size + 1
            total_batches = (len(image_paths) + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_number}/{total_batches} ({len(batch)} images)")
            
            for image_path in batch:
                detections = self.process_single_image(image_path, confidence_threshold)
                all_detections.extend(detections)
                processed_count += 1
            
            # Log progress
            progress = (processed_count / len(image_paths)) * 100
            logger.info(f"Progress: {processed_count}/{len(image_paths)} images ({progress:.1f}%)")
        
        # Convert to DataFrame
        if all_detections:
            df = pd.DataFrame([vars(d) for d in all_detections])
            logger.info(f"Total detections: {len(df)}")
            
            # Save results
            self._save_results(df)
            
            return df
        else:
            logger.warning("No detections found in any images")
            return pd.DataFrame()
    
    def _save_results(self, df: pd.DataFrame):
        """Save detection results to multiple formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as Parquet (efficient for large datasets)
        parquet_path = self.output_dir / f"detections_{timestamp}.parquet"
        df.to_parquet(parquet_path, index=False)
        logger.info(f"Saved {len(df)} detections to Parquet: {parquet_path}")
        
        # Save as JSON (for debugging and manual inspection)
        json_path = self.output_dir / f"detections_{timestamp}.json"
        df.to_json(json_path, orient='records', indent=2)
        logger.info(f"Saved detections to JSON: {json_path}")
        
        # Save summary statistics
        summary = self._generate_summary(df)
        summary_path = self.output_dir / f"summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(f"Saved summary to: {summary_path}")
        
        # Save CSV (optional, for Excel users)
        csv_path = self.output_dir / f"detections_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved detections to CSV: {csv_path}")
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics from detection results"""
        if df.empty:
            return {"message": "No detections found"}
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_images_processed": df['image_path'].nunique(),
            "total_detections": len(df),
            "detections_per_image": len(df) / df['image_path'].nunique(),
            "detections_by_class": df['detected_class'].value_counts().to_dict(),
            "detections_by_channel": df['channel_name'].value_counts().to_dict(),
            "confidence_statistics": {
                "mean": float(df['confidence'].mean()),
                "median": float(df['confidence'].median()),
                "min": float(df['confidence'].min()),
                "max": float(df['confidence'].max()),
                "std": float(df['confidence'].std())
            },
            "top_detections": df.nlargest(10, 'confidence')[['image_name', 'detected_class', 'confidence']].to_dict('records')
        }
        
        return summary

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='YOLOv8 Image Detection Pipeline')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Path to YOLO model weights (default: yolov8n.pt)')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size for processing (default: 16)')
    parser.add_argument('--confidence', type=float, default=0.25,
                       help='Minimum confidence threshold (default: 0.25)')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cuda', 'cpu'],
                       help='Device to run inference on (default: cpu)')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory for results')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    
    return parser.parse_args()

def main():
    """Main execution function for YOLO enrichment pipeline"""
    args = parse_arguments()
    
    # Configure logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    logger.info("=" * 60)
    logger.info("Starting YOLO Image Detection Pipeline")
    logger.info("=" * 60)
    
    try:
        # Initialize detector
        detector = YOLODetector(
            model_path=args.model,
            device=args.device
        )
        
        # Override output directory if specified
        if args.output_dir:
            detector.output_dir = Path(args.output_dir)
            detector.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process images
        start_time = datetime.now()
        detections_df = detector.process_batch(
            batch_size=args.batch_size,
            confidence_threshold=args.confidence
        )
        end_time = datetime.now()
        
        # Calculate processing time
        processing_time = (end_time - start_time).total_seconds()
        
        if not detections_df.empty:
            logger.info(f"Processing completed in {processing_time:.2f} seconds")
            logger.info(f"Processed {detections_df['image_path'].nunique()} images")
            logger.info(f"Found {len(detections_df)} total detections")
            
            # Print summary
            summary = detector._generate_summary(detections_df)
            logger.info("\nDetection Summary:")
            logger.info(f"  Total images processed: {summary['total_images_processed']}")
            logger.info(f"  Total detections: {summary['total_detections']}")
            logger.info(f"  Detections per image: {summary['detections_per_image']:.2f}")
            
            logger.info("\nTop detected classes:")
            for class_name, count in list(summary['detections_by_class'].items())[:5]:
                logger.info(f"  {class_name}: {count}")
            
        else:
            logger.warning("No detections found. Check your image directory and model.")
        
        logger.info("\n" + "=" * 60)
        logger.info("YOLO Detection Pipeline Completed")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
