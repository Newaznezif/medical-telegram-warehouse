"""
Configuration management for the pipeline.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import yaml
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DetectionClass(Enum):
    """YOLO detection classes."""
    MEDICAL = "medical"
    COSMETIC = "cosmetic"
    PACKAGING = "packaging"
    PERSON = "person"
    TEXT = "text"
    OTHER = "other"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    name: str = field(default_factory=lambda: os.getenv("DB_NAME", "medical_warehouse"))
    user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", "postgres"))
    pool_size: int = 20
    max_overflow: int = 40
    pool_recycle: int = 3600
    
    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_url(self) -> str:
        """Get async database URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class TelegramConfig:
    """Telegram API configuration."""
    api_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_API_ID", ""))
    api_hash: str = field(default_factory=lambda: os.getenv("TELEGRAM_API_HASH", ""))
    session_name: str = "telegram_session"
    channels: List[str] = field(default_factory=lambda: [
        "@chemed123",
        "@lobelia4cosmetics",
        "@tikvahpharma"
    ])
    request_delay: int = 1  # seconds between requests
    max_retries: int = 3
    timeout: int = 30  # seconds


@dataclass
class YOLOConfig:
    """YOLO model configuration."""
    model_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    batch_size: int = 16
    img_size: int = 640
    classes: List[str] = field(default_factory=lambda: [
        "medical",
        "cosmetic",
        "packaging",
        "person",
        "text"
    ])
    
    @property
    def model_weights(self) -> str:
        """Get model weights path."""
        if Path(self.model_path).exists():
            return self.model_path
        # Download if not exists
        return self.model_path


@dataclass
class APIConfig:
    """FastAPI configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 4
    title: str = "Medical Telegram Warehouse API"
    version: str = "1.0.0"
    description: str = "API for medical/cosmetic Telegram data analytics"
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    @property
    def docs_url(self) -> str:
        """Get docs URL."""
        return f"http://{self.host}:{self.port}/docs"
    
    @property
    def redoc_url(self) -> str:
        """Get ReDoc URL."""
        return f"http://{self.host}:{self.port}/redoc"


@dataclass
class PipelineConfig:
    """Pipeline configuration."""
    environment: Environment = Environment.DEVELOPMENT
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    timeout: int = 3600  # seconds
    dagster_host: str = "0.0.0.0"
    dagster_port: int = 3000
    log_level: str = "INFO"
    data_dir: Path = Path("data")
    reports_dir: Path = Path("reports")
    backups_dir: Path = Path("backups")
    temp_dir: Path = Path("temp")
    
    def __post_init__(self):
        """Create directories after initialization."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    enable_health_checks: bool = True
    health_check_interval: int = 60  # seconds
    enable_alerts: bool = True
    alert_email: Optional[str] = None
    alert_webhook: Optional[str] = None
    metrics_retention_days: int = 30


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", "your-secret-key-here")
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    enable_https: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None


@dataclass
class Config:
    """Main configuration class."""
    
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    yolo: YOLOConfig = field(default_factory=YOLOConfig)
    api: APIConfig = field(default_factory=APIConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Runtime settings
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    testing: bool = field(default_factory=lambda: os.getenv("TESTING", "False").lower() == "true")
    
    @classmethod
    def from_yaml(cls, config_path: str = "config.yaml") -> "Config":
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            # Create default config
            default_config = cls()
            default_config.save_yaml(config_path)
            return default_config
        
        with open(config_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        # Convert to Config object
        return cls(
            database=DatabaseConfig(**yaml_data.get("database", {})),
            telegram=TelegramConfig(**yaml_data.get("telegram", {})),
            yolo=YOLOConfig(**yaml_data.get("yolo", {})),
            api=APIConfig(**yaml_data.get("api", {})),
            pipeline=PipelineConfig(**yaml_data.get("pipeline", {})),
            monitoring=MonitoringConfig(**yaml_data.get("monitoring", {})),
            security=SecurityConfig(**yaml_data.get("security", {})),
            debug=yaml_data.get("debug", False),
            testing=yaml_data.get("testing", False),
        )
    
    def save_yaml(self, config_path: str = "config.yaml") -> None:
        """Save configuration to YAML file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = {
            "database": asdict(self.database),
            "telegram": asdict(self.telegram),
            "yolo": asdict(self.yolo),
            "api": asdict(self.api),
            "pipeline": asdict(self.pipeline),
            "monitoring": asdict(self.monitoring),
            "security": asdict(self.security),
            "debug": self.debug,
            "testing": self.testing,
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate Telegram credentials
        if not self.telegram.api_id or not self.telegram.api_hash:
            errors.append("Telegram API ID and Hash are required")
        
        # Validate database connection
        if not all([
            self.database.host,
            self.database.port,
            self.database.name,
            self.database.user,
            self.database.password,
        ]):
            errors.append("Database configuration is incomplete")
        
        # Validate YOLO model path
        yolo_path = Path(self.yolo.model_path)
        if not yolo_path.exists() and not yolo_path.name.startswith("yolov8"):
            errors.append(f"YOLO model not found: {self.yolo.model_path}")
        
        # Validate directories
        for dir_path in [
            self.pipeline.data_dir,
            self.pipeline.reports_dir,
            self.pipeline.backups_dir,
        ]:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {dir_path}: {str(e)}")
        
        return errors
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for the configuration."""
        return {
            "DATABASE_URL": self.database.url,
            "TELEGRAM_API_ID": self.telegram.api_id,
            "TELEGRAM_API_HASH": self.telegram.api_hash,
            "API_HOST": self.api.host,
            "API_PORT": str(self.api.port),
            "DEBUG": str(self.debug),
            "ENVIRONMENT": self.pipeline.environment.value,
            "LOG_LEVEL": self.pipeline.log_level,
            "SECRET_KEY": self.security.secret_key,
        }


# Global configuration instance
config = Config.from_yaml()


def get_config() -> Config:
    """Get current configuration."""
    return config


def reload_config(config_path: str = "config.yaml") -> Config:
    """Reload configuration from file."""
    global config
    config = Config.from_yaml(config_path)
    return config


def print_config_summary() -> None:
    """Print configuration summary."""
    print("=" * 60)
    print("Medical Telegram Warehouse Configuration")
    print("=" * 60)
    
    cfg = get_config()
    
    print(f"\n📊 Environment: {cfg.pipeline.environment.value}")
    print(f"🔧 Debug Mode: {cfg.debug}")
    print(f"🧪 Testing Mode: {cfg.testing}")
    
    print(f"\n📁 Directories:")
    print(f"   Data: {cfg.pipeline.data_dir}")
    print(f"   Reports: {cfg.pipeline.reports_dir}")
    print(f"   Backups: {cfg.pipeline.backups_dir}")
    
    print(f"\n🗄️  Database:")
    print(f"   Host: {cfg.database.host}:{cfg.database.port}")
    print(f"   Name: {cfg.database.name}")
    print(f"   User: {cfg.database.user}")
    
    print(f"\n📱 Telegram:")
    print(f"   API ID: {'*' * len(cfg.telegram.api_id) if cfg.telegram.api_id else 'Not set'}")
    print(f"   Channels: {', '.join(cfg.telegram.channels)}")
    
    print(f"\n🔍 YOLO Detection:")
    print(f"   Model: {cfg.yolo.model_path}")
    print(f"   Confidence: {cfg.yolo.confidence_threshold}")
    print(f"   Classes: {', '.join(cfg.yolo.classes)}")
    
    print(f"\n🌐 API:")
    print(f"   Host: {cfg.api.host}:{cfg.api.port}")
    print(f"   Docs: {cfg.api.docs_url}")
    
    print(f"\n⚡ Pipeline:")
    print(f"   Max Retries: {cfg.pipeline.max_retries}")
    print(f"   Timeout: {cfg.pipeline.timeout}s")
    print(f"   Log Level: {cfg.pipeline.log_level}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Test the configuration
    print_config_summary()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ Configuration is valid")
    
    # Save example environment file
    env_vars = config.get_environment_vars()
    env_file = Path(".env.example")
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"\n📄 Example environment file created: {env_file}")
