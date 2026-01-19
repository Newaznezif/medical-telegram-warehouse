"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class TimeRange(str, Enum):
    """Time range for analytics"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class ChannelCategory(str, Enum):
    """Channel categories"""
    MEDICAL = "medical"
    COSMETIC = "cosmetic"
    MIXED = "mixed"
    OTHER = "other"

class ObjectCategory(str, Enum):
    """Object categories"""
    MEDICAL = "medical"
    COSMETIC = "cosmetic"
    PACKAGING = "packaging"
    OTHER = "other"

# Health schemas
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    database: bool

# Report schemas
class ReportRequest(BaseModel):
    """Request schema for generating reports"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    channel_names: Optional[List[str]] = None
    object_categories: Optional[List[ObjectCategory]] = None
    time_range: TimeRange = TimeRange.MONTH
    include_details: bool = False
    
    @validator('end_date', always=True)
    def validate_dates(cls, v, values):
        """Validate date range"""
        if 'start_date' in values and values['start_date'] and v:
            if v < values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v

class DetectionStats(BaseModel):
    """Detection statistics"""
    total_detections: int
    unique_images: int
    unique_channels: int
    unique_objects: int
    avg_confidence: float
    high_confidence_count: int
    high_confidence_percent: float

class ChannelStats(BaseModel):
    """Channel statistics"""
    channel_name: str
    category: Optional[ChannelCategory]
    detection_count: int
    unique_objects: int
    avg_confidence: float
    medical_percent: float
    cosmetic_percent: float

class ObjectStats(BaseModel):
    """Object statistics"""
    object_name: str
    category: ObjectCategory
    detection_count: int
    unique_channels: int
    avg_confidence: float
    channel_distribution: Dict[str, int]

class TimeSeriesPoint(BaseModel):
    """Time series data point"""
    date: date
    count: int
    avg_confidence: float

class ReportResponse(BaseModel):
    """Report response"""
    summary: DetectionStats
    channels: List[ChannelStats]
    top_objects: List[ObjectStats]
    time_series: List[TimeSeriesPoint]
    generated_at: datetime
    parameters: Dict[str, Any]

# Channel schemas
class ChannelBase(BaseModel):
    """Base channel schema"""
    name: str
    display_name: Optional[str] = None
    category: ChannelCategory = ChannelCategory.OTHER
    description: Optional[str] = None
    is_active: bool = True

class ChannelCreate(ChannelBase):
    """Channel creation schema"""
    pass

class ChannelUpdate(BaseModel):
    """Channel update schema"""
    display_name: Optional[str] = None
    category: Optional[ChannelCategory] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ChannelResponse(ChannelBase):
    """Channel response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    detection_count: int = 0
    
    class Config:
        from_attributes = True

class ChannelListResponse(BaseModel):
    """Channel list response"""
    items: List[ChannelResponse]
    total: int
    page: int
    size: int
    pages: int

# Search schemas
class SearchRequest(BaseModel):
    """Search request"""
    query: str
    channel_names: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)
    max_confidence: Optional[float] = Field(None, ge=0, le=1)
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

class SearchResult(BaseModel):
    """Search result"""
    image_path: str
    image_name: str
    channel_name: str
    detected_class: str
    confidence: float
    detection_date: Optional[datetime]
    bounding_box: Dict[str, float]
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    """Search response"""
    results: List[SearchResult]
    total: int
    query: str
    search_time_ms: float

# Error schemas
class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    code: int
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseModel):
    """Success response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime
