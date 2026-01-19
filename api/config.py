import os
from typing import List, Optional
from pydantic import BaseSettings, validator, PostgresDsn

class Settings(BaseSettings):
    """Application settings using Pydantic v1"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Telegram Medical Warehouse API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    API_KEY: str = "dev-api-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        
        # Build from environment variables or use defaults
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "medical_warehouse")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # File Paths (from Task 3)
    IMAGE_BASE_PATH: str = "data/raw/images"
    DETECTION_OUTPUT_PATH: str = "data/processed/detections"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"Warning: Failed to load settings from .env: {e}")
    # Use defaults
    settings = Settings(
        DATABASE_URL="postgresql://postgres:postgres@localhost:5432/medical_warehouse"
    )
