from sqlalchemy import Column, String, Text, Integer
from api.models.base import BaseModel

class Channel(BaseModel):
    """Telegram channel model"""
    __tablename__ = "dim_channels"
    
    channel_key = Column(String(100), unique=True, index=True, nullable=False)
    channel_name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Statistics (cached for performance)
    total_messages = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_forwards = Column(Integer, default=0)
    active_days = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Channel {self.channel_name}>"
