from sqlalchemy import (
    Column, String, Float, Integer, Text, 
    DateTime, Index, Boolean, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from api.models.base import BaseModel
import uuid

class RawImageDetection(BaseModel):
    """Raw YOLO detection results"""
    __tablename__ = "raw_image_detections"
    
    detection_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    image_path = Column(Text, nullable=False)
    image_name = Column(String(255), nullable=False, index=True)
    channel_name = Column(String(100), nullable=False, index=True)
    date_str = Column(String(10), nullable=False, index=True)
    detected_class = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False, index=True)
    x_center = Column(Float, nullable=False)
    y_center = Column(Float, nullable=False)
    box_width = Column(Float, nullable=False)
    box_height = Column(Float, nullable=False)
    original_width = Column(Integer, nullable=False)
    original_height = Column(Integer, nullable=False)
    processed_at = Column(DateTime, nullable=False)
    product_category = Column(String(50), index=True)
    confidence_level = Column(String(20), index=True)
    
    __table_args__ = (
        Index('idx_channel_date', 'channel_name', 'date_str'),
        Index('idx_class_confidence', 'detected_class', 'confidence'),
        Index('idx_detection_processed', 'processed_at'),
    )
    
    def __repr__(self):
        return f"<RawDetection {self.detected_class} ({self.confidence:.2f})>"

class DetectionAggregate(BaseModel):
    """Aggregated detection statistics"""
    __tablename__ = "detection_aggregates"
    
    aggregate_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    channel_key = Column(String(100), nullable=False, index=True)
    channel_name = Column(String(255), nullable=False, index=True)
    date_key = Column(Integer, nullable=False, index=True)
    full_date = Column(DateTime, nullable=False, index=True)
    detected_class = Column(String(100), nullable=False, index=True)
    product_category = Column(String(50), index=True)
    detection_count = Column(Integer, nullable=False, default=0)
    unique_images_count = Column(Integer, nullable=False, default=0)
    avg_confidence = Column(Float, nullable=False)
    min_confidence = Column(Float, nullable=False)
    max_confidence = Column(Float, nullable=False)
    std_confidence = Column(Float, nullable=True)
    high_confidence_count = Column(Integer, default=0)
    medium_confidence_count = Column(Integer, default=0)
    low_confidence_count = Column(Integer, default=0)
    avg_x_center = Column(Float)
    avg_y_center = Column(Float)
    avg_box_area = Column(Float)
    
    __table_args__ = (
        Index('idx_aggregate_unique', 'channel_key', 'date_key', 'detected_class', unique=True),
        Index('idx_aggregate_category', 'product_category', 'full_date'),
    )
    
    def __repr__(self):
        return f"<DetectionAggregate {self.detected_class} x{self.detection_count}>"
