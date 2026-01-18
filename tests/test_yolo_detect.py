"""
Unit tests for YOLO detection system - Standalone version
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import sys

# Mock DetectionResult class for testing
@dataclass
class DetectionResult:
    """Mock detection result data class"""
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
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'image_path': self.image_path,
            'image_name': self.image_name,
            'channel_name': self.channel_name,
            'date_str': self.date_str,
            'detected_class': self.detected_class,
            'confidence': self.confidence,
            'x_center': self.x_center,
            'y_center': self.y_center,
            'box_width': self.box_width,
            'box_height': self.box_height,
            'original_width': self.original_width,
            'original_height': self.original_height,
            'processed_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def to_dataframe(detections: List['DetectionResult']) -> pd.DataFrame:
        """Convert list of detections to DataFrame"""
        return pd.DataFrame([d.to_dict() for d in detections])

class TestDetectionResult:
    """Test the DetectionResult data class"""
    
    def test_detection_result_creation(self):
        """Test creating a DetectionResult object"""
        detection = DetectionResult(
            image_path="test.jpg",
            image_name="test.jpg",
            channel_name="test_channel",
            date_str="2024-01-15",
            detected_class="bottle",
            confidence=0.85,
            x_center=0.5,
            y_center=0.5,
            box_width=0.2,
            box_height=0.3,
            original_width=640,
            original_height=480
        )
        
        assert detection.image_path == "test.jpg"
        assert detection.detected_class == "bottle"
        assert detection.confidence == 0.85
        assert detection.x_center == 0.5
        assert detection.y_center == 0.5
        assert detection.box_width == 0.2
        assert detection.box_height == 0.3
    
    def test_detection_result_to_dict(self):
        """Test converting DetectionResult to dictionary"""
        detection = DetectionResult(
            image_path="test.jpg",
            image_name="test.jpg",
            channel_name="test_channel",
            date_str="2024-01-15",
            detected_class="bottle",
            confidence=0.85,
            x_center=0.5,
            y_center=0.5,
            box_width=0.2,
            box_height=0.3,
            original_width=640,
            original_height=480
        )
        
        detection_dict = detection.to_dict()
        assert isinstance(detection_dict, dict)
        assert detection_dict["image_path"] == "test.jpg"
        assert detection_dict["detected_class"] == "bottle"
        assert detection_dict["confidence"] == 0.85
    
    def test_detection_result_to_dataframe(self):
        """Test converting multiple detections to DataFrame"""
        detections = [
            DetectionResult(
                image_path="test1.jpg",
                image_name="test1.jpg",
                channel_name="channel1",
                date_str="2024-01-15",
                detected_class="bottle",
                confidence=0.85,
                x_center=0.5,
                y_center=0.5,
                box_width=0.2,
                box_height=0.3,
                original_width=640,
                original_height=480
            ),
            DetectionResult(
                image_path="test2.jpg",
                image_name="test2.jpg",
                channel_name="channel2",
                date_str="2024-01-15",
                detected_class="box",
                confidence=0.75,
                x_center=0.6,
                y_center=0.4,
                box_width=0.3,
                box_height=0.2,
                original_width=800,
                original_height=600
            )
        ]
        
        df = DetectionResult.to_dataframe(detections)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "detected_class" in df.columns
        assert "confidence" in df.columns
        assert df["confidence"].iloc[0] == 0.85
        assert df["confidence"].iloc[1] == 0.75

class TestDataValidation:
    """Test data validation and quality checks"""
    
    def test_detection_data_validation(self):
        """Test that detection data meets quality standards"""
        # Valid detection
        valid_detection = DetectionResult(
            image_path="test.jpg",
            image_name="test.jpg",
            channel_name="test_channel",
            date_str="2024-01-15",
            detected_class="bottle",
            confidence=0.85,
            x_center=0.5,
            y_center=0.5,
            box_width=0.2,
            box_height=0.3,
            original_width=640,
            original_height=480
        )
        
        # Test confidence bounds
        assert 0 <= valid_detection.confidence <= 1
        
        # Test normalized coordinates
        assert 0 <= valid_detection.x_center <= 1
        assert 0 <= valid_detection.y_center <= 1
        assert 0 <= valid_detection.box_width <= 1
        assert 0 <= valid_detection.box_height <= 1
        
        # Test positive dimensions
        assert valid_detection.original_width > 0
        assert valid_detection.original_height > 0
    
    def test_dataframe_validation(self):
        """Test DataFrame validation"""
        # Create test DataFrame with both valid and invalid data
        test_data = {
            'image_path': ['img1.jpg', 'img2.jpg', 'img3.jpg'],
            'detected_class': ['bottle', 'box', 'medicine'],
            'confidence': [0.85, 1.5, -0.1],  # One invalid (>1), one invalid (<0)
            'x_center': [0.5, 1.2, 0.3],  # One invalid (>1)
            'y_center': [0.5, 0.4, 0.6],
            'box_width': [0.2, 0.3, 0.4],
            'box_height': [0.3, 0.2, 0.5]
        }
        
        df = pd.DataFrame(test_data)
        
        # Test validation functions
        valid_confidences = df['confidence'].between(0, 1)
        assert valid_confidences.sum() == 1  # Only first row valid
        
        valid_x = df['x_center'].between(0, 1)
        assert valid_x.sum() == 2  # First and third rows valid

class TestDataProcessing:
    """Test data processing functions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.test_dir) / "output"
        self.output_dir.mkdir()
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_save_detections_json(self):
        """Test saving detections to JSON"""
        detections = [
            DetectionResult(
                image_path="test1.jpg",
                image_name="test1.jpg",
                channel_name="channel1",
                date_str="2024-01-15",
                detected_class="bottle",
                confidence=0.85,
                x_center=0.5,
                y_center=0.5,
                box_width=0.2,
                box_height=0.3,
                original_width=640,
                original_height=480
            )
        ]
        
        # Convert to DataFrame
        df = DetectionResult.to_dataframe(detections)
        
        # Save to JSON
        json_path = self.output_dir / "detections.json"
        df.to_json(json_path, orient='records', indent=2)
        
        assert json_path.exists()
        
        # Load and verify
        with open(json_path, 'r') as f:
            loaded = json.load(f)
        
        assert len(loaded) == 1
        assert loaded[0]['detected_class'] == 'bottle'
    
    def test_save_detections_csv(self):
        """Test saving detections to CSV"""
        detections = [
            DetectionResult(
                image_path="test1.jpg",
                image_name="test1.jpg",
                channel_name="channel1",
                date_str="2024-01-15",
                detected_class="bottle",
                confidence=0.85,
                x_center=0.5,
                y_center=0.5,
                box_width=0.2,
                box_height=0.3,
                original_width=640,
                original_height=480
            )
        ]
        
        # Convert to DataFrame
        df = DetectionResult.to_dataframe(detections)
        
        # Save to CSV
        csv_path = self.output_dir / "detections.csv"
        df.to_csv(csv_path, index=False)
        
        assert csv_path.exists()
        
        # Load and verify
        loaded_df = pd.read_csv(csv_path)
        assert len(loaded_df) == 1
        assert loaded_df['detected_class'].iloc[0] == 'bottle'
    
    def test_save_detections_parquet(self):
        """Test saving detections to Parquet"""
        detections = [
            DetectionResult(
                image_path="test1.jpg",
                image_name="test1.jpg",
                channel_name="channel1",
                date_str="2024-01-15",
                detected_class="bottle",
                confidence=0.85,
                x_center=0.5,
                y_center=0.5,
                box_width=0.2,
                box_height=0.3,
                original_width=640,
                original_height=480
            )
        ]
        
        # Convert to DataFrame
        df = DetectionResult.to_dataframe(detections)
        
        # Save to Parquet
        parquet_path = self.output_dir / "detections.parquet"
        df.to_parquet(parquet_path, index=False)
        
        assert parquet_path.exists()
        
        # Load and verify
        loaded_df = pd.read_parquet(parquet_path)
        assert len(loaded_df) == 1
        assert loaded_df['detected_class'].iloc[0] == 'bottle'

class TestBusinessLogic:
    """Test business logic for medical/cosmetic detection"""
    
    def test_categorize_medical_objects(self):
        """Test categorization of medical objects"""
        # Medical keywords
        medical_keywords = ['medicine', 'pill', 'syringe', 'medical_device', 'drug', 'pharmacy', 'tablet']
        cosmetic_keywords = ['cosmetic', 'cream', 'ointment', 'lotion', 'makeup']
        packaging_keywords = ['box', 'package', 'container', 'packaging', 'bottle']
        
        def categorize_object(obj_name):
            obj_lower = str(obj_name).lower()
            if any(keyword in obj_lower for keyword in medical_keywords):
                return 'Medical'
            elif any(keyword in obj_lower for keyword in cosmetic_keywords):
                return 'Cosmetic'
            elif any(keyword in obj_lower for keyword in packaging_keywords):
                return 'Packaging'
            else:
                return 'Other'
        
        # Test cases - FIXED: 'bottle' is in packaging_keywords, 'cream' is in cosmetic_keywords
        test_cases = [
            ('medicine bottle', 'Medical'),  # 'medicine' triggers Medical
            ('pill container', 'Medical'),    # 'pill' triggers Medical
            ('face cream', 'Cosmetic'),       # 'cream' triggers Cosmetic
            ('cosmetic box', 'Cosmetic'),     # 'cosmetic' triggers Cosmetic
            ('shipping box', 'Packaging'),    # 'box' triggers Packaging
            ('plastic bottle', 'Packaging'),  # 'bottle' triggers Packaging
            ('random object', 'Other')
        ]
        
        for obj_name, expected_category in test_cases:
            assert categorize_object(obj_name) == expected_category, f"Failed for: {obj_name}"
    
    def test_confidence_quality_buckets(self):
        """Test categorizing detections by confidence quality"""
        # Create test detections with different confidence levels
        detections = [
            DetectionResult(
                image_path=f"test_{i}.jpg",
                image_name=f"test_{i}.jpg",
                channel_name="test",
                date_str="2024-01-15",
                detected_class="object",
                confidence=conf,
                x_center=0.5,
                y_center=0.5,
                box_width=0.2,
                box_height=0.3,
                original_width=640,
                original_height=480
            )
            for i, conf in enumerate([0.2, 0.4, 0.6, 0.8, 0.9])
        ]
        
        df = DetectionResult.to_dataframe(detections)
        
        # Categorize by confidence - FIXED: Check pandas cut behavior
        # pandas.cut bins are (0, 0.5], (0.5, 0.8], (0.8, 1.0]
        # So 0.5 goes to first bin, 0.8 goes to second bin
        df['confidence_level'] = pd.cut(
            df['confidence'],
            bins=[0, 0.5, 0.8, 1.0],
            labels=['Low', 'Medium', 'High'],
            right=True  # Default: intervals are closed on the right
        )
        
        # Count by level
        level_counts = df['confidence_level'].value_counts()
        
        # Verify counts
        # With bins [0, 0.5], (0.5, 0.8], (0.8, 1.0]:
        # 0.2 -> Low, 0.4 -> Low, 0.6 -> Medium, 0.8 -> Medium, 0.9 -> High
        assert level_counts.get('Low', 0) == 2  # 0.2, 0.4
        assert level_counts.get('Medium', 0) == 2  # 0.6, 0.8
        assert level_counts.get('High', 0) == 1  # 0.9
        
        # Alternatively, use right=False to get different binning
        df['confidence_level_right_false'] = pd.cut(
            df['confidence'],
            bins=[0, 0.5, 0.8, 1.0],
            labels=['Low', 'Medium', 'High'],
            right=False  # Intervals are closed on the left: [0, 0.5), [0.5, 0.8), [0.8, 1.0)
        )
        
        level_counts2 = df['confidence_level_right_false'].value_counts()
        # With bins [0, 0.5), [0.5, 0.8), [0.8, 1.0):
        # 0.2 -> Low, 0.4 -> Low, 0.6 -> Medium, 0.8 -> High, 0.9 -> High
        assert level_counts2.get('Low', 0) == 2  # 0.2, 0.4
        assert level_counts2.get('Medium', 0) == 1  # 0.6
        assert level_counts2.get('High', 0) == 2  # 0.8, 0.9

class TestStatistics:
    """Test statistical calculations"""
    
    def test_basic_statistics(self):
        """Test basic statistical calculations"""
        # Create test data with varying confidences
        np.random.seed(42)
        confidences = np.random.uniform(0.3, 0.95, 100)
        
        detections = [
            DetectionResult(
                image_path=f"test_{i}.jpg",
                image_name=f"test_{i}.jpg",
                channel_name="test",
                date_str="2024-01-15",
                detected_class=np.random.choice(['bottle', 'box', 'medicine']),
                confidence=float(conf),
                x_center=0.5,
                y_center=0.5,
                box_width=0.2,
                box_height=0.3,
                original_width=640,
                original_height=480
            )
            for i, conf in enumerate(confidences)
        ]
        
        df = DetectionResult.to_dataframe(detections)
        
        # Calculate statistics
        stats = {
            'mean_confidence': df['confidence'].mean(),
            'median_confidence': df['confidence'].median(),
            'std_confidence': df['confidence'].std(),
            'min_confidence': df['confidence'].min(),
            'max_confidence': df['confidence'].max(),
            'total_detections': len(df),
            'unique_classes': df['detected_class'].nunique()
        }
        
        # Verify statistics are reasonable
        assert 0 <= stats['mean_confidence'] <= 1
        assert 0 <= stats['median_confidence'] <= 1
        assert stats['min_confidence'] >= 0.3  # From our random generation
        assert stats['max_confidence'] <= 0.95  # From our random generation
        assert stats['total_detections'] == 100
        assert 1 <= stats['unique_classes'] <= 3

class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_data_pipeline(self):
        """Test a complete data pipeline from creation to analysis"""
        # Step 1: Create synthetic data
        np.random.seed(42)
        n_samples = 50
        
        detections = []
        for i in range(n_samples):
            detections.append(DetectionResult(
                image_path=f"channel_{i%3}/img_{i}.jpg",
                image_name=f"img_{i}.jpg",
                channel_name=f"channel_{i%3}",
                date_str=f"2024-01-{15 + i%5:02d}",
                detected_class=np.random.choice(['medicine', 'pill', 'cream', 'bottle', 'box']),
                confidence=np.random.uniform(0.3, 0.95),
                x_center=np.random.uniform(0, 1),
                y_center=np.random.uniform(0, 1),
                box_width=np.random.uniform(0.1, 0.3),
                box_height=np.random.uniform(0.1, 0.3),
                original_width=640,
                original_height=480
            ))
        
        # Step 2: Convert to DataFrame
        df = DetectionResult.to_dataframe(detections)
        
        # Step 3: Add categorization
        medical_keywords = ['medicine', 'pill']
        cosmetic_keywords = ['cream']
        packaging_keywords = ['bottle', 'box']
        
        def categorize(obj):
            obj_lower = str(obj).lower()
            # Check in order: Medical > Cosmetic > Packaging
            if any(kw in obj_lower for kw in medical_keywords):
                return 'Medical'
            elif any(kw in obj_lower for kw in cosmetic_keywords):
                return 'Cosmetic'
            elif any(kw in obj_lower for kw in packaging_keywords):
                return 'Packaging'
            return 'Other'
        
        df['category'] = df['detected_class'].apply(categorize)
        
        # Step 4: Add confidence levels
        df['confidence_level'] = pd.cut(
            df['confidence'],
            bins=[0, 0.5, 0.8, 1.0],
            labels=['Low', 'Medium', 'High'],
            right=True
        )
        
        # Step 5: Calculate statistics
        stats = {
            'total': len(df),
            'medical_count': (df['category'] == 'Medical').sum(),
            'cosmetic_count': (df['category'] == 'Cosmetic').sum(),
            'packaging_count': (df['category'] == 'Packaging').sum(),
            'high_confidence_pct': (df['confidence'] >= 0.8).sum() / len(df) * 100,
            'avg_confidence': df['confidence'].mean()
        }
        
        # Verify pipeline worked
        assert len(df) == n_samples
        assert stats['total'] == n_samples
        assert 0 <= stats['high_confidence_pct'] <= 100
        assert 0 <= stats['avg_confidence'] <= 1

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
