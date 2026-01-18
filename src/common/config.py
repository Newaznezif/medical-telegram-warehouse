import os
from dotenv import load_dotenv
from typing import List  # <-- ADD THIS
from typing import Dict, Any

load_dotenv()

class Config:
    """Application configuration"""
    
    # Telegram API
    TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
    TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
    TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'medical_warehouse')
    DB_USER = os.getenv('DB_USER', 'admin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin123')
    
    # Paths
    RAW_DATA_PATH = os.getenv('RAW_DATA_PATH', './data/raw')
    PROCESSED_DATA_PATH = os.getenv('PROCESSED_DATA_PATH', './data/processed')
    LOG_PATH = os.getenv('LOG_PATH', './logs')
    
    # Channels to scrape
    TELEGRAM_CHANNELS = [
        channel.strip() 
        for channel in os.getenv('TELEGRAM_CHANNELS', '').split(',') 
        if channel.strip()
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
        missing = [var for var in required if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database connection URL"""
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )
    
    @classmethod
    def get_telegram_channels(cls) -> List[str]:
        """Get list of channels to scrape"""
        return cls.TELEGRAM_CHANNELS or [
            "@CheMed123",
            "@lobelia4cosmetics", 
            "@tikvahpharma"
        ]

config = Config()
