from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from api.models.base import BaseModel
import uuid

class Message(BaseModel):
    """Telegram message model"""
    __tablename__ = "fct_messages"
    
    message_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    channel_key = Column(String(100), nullable=False, index=True)
    channel_name = Column(String(255), nullable=False, index=True)
    date_key = Column(Integer, nullable=False, index=True)
    full_date = Column(DateTime, nullable=False, index=True)
    message_text = Column(Text, nullable=False)
    message_timestamp = Column(DateTime, nullable=False, index=True)
    views = Column(Integer, default=0)
    forwards = Column(Integer, default=0)
    has_image = Column(Boolean, default=False)
    image_url = Column(String(500), nullable=True)
    image_path = Column(String(500), nullable=True)
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    hashtags = Column(JSON)
    mentions = Column(JSON)
    is_processed = Column(Boolean, default=False)
    has_detections = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_message_channel_date', 'channel_key', 'date_key'),
        Index('idx_message_timestamp', 'message_timestamp'),
        Index('idx_message_engagement', 'views', 'forwards'),
    )
    
    def __repr__(self):
        return f"<Message {self.message_id[:8]}...>"
