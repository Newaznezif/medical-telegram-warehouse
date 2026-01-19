"""
Shared configuration for Medical Telegram Warehouse
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, Field, validator
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Project
    PROJECT_NAME: str = "Medical Telegram Warehouse API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
        ],
        env="CORS_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost/medical_warehouse",
        env="DATABASE_URL"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # File Upload
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    
    # Analytics
    ANALYTICS_CACHE_TTL: int = Field(default=300, env="ANALYTICS_CACHE_TTL")  # 5 minutes
    
    # YOLO
    YOLO_MODEL_PATH: str = Field(default="yolov8n.pt", env="YOLO_MODEL_PATH")
    YOLO_CONFIDENCE_THRESHOLD: float = Field(default=0.5, env="YOLO_CONFIDENCE_THRESHOLD")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

# Global settings instance
settings = Settings()

# Environment-specific overrides
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    settings.LOG_LEVEL = "WARNING"
elif settings.ENVIRONMENT == "staging":
    settings.DEBUG = False
    settings.LOG_LEVEL = "INFO"
else:  # development
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
