import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# File Paths
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
MESSAGES_PATH = RAW_DATA_PATH / "telegram_messages"
IMAGES_PATH = RAW_DATA_PATH / "images"

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "medical_warehouse")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")

# Telegram Configuration
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
TELEGRAM_CHANNELS = [
    "@CheMed123",
    "@lobelia4cosmetics",
    "@BusinessInfoEth",
    "@yetenaweg",
    "@EAHPA",
]

# Scraping Thresholds
MAX_MESSAGES_PER_CHANNEL = 500
SCRAPE_DELAY_SECONDS = 1

# KPI Thresholds
ANOMALY_CONFIDENCE_THRESHOLD = 0.5
RISK_SCORE_THRESHOLD = 0.7
