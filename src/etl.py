import json
import psycopg2
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from src.config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    MESSAGES_PATH, TELEGRAM_CHANNELS
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ingest_data() -> List[Dict[str, Any]]:
    """
    Simulate ingestion by reading existing JSON files or placeholder for scraper.
    In a real scenario, this would call the TelegramScraper.
    """
    logger.info("ingesting data from raw JSON files...")
    all_messages = []
    
    # Check if directory exists
    if not MESSAGES_PATH.exists():
        logger.warning(f"Messages path {MESSAGES_PATH} does not exist. Returning empty list.")
        return []

    # Iterate through date-partitioned folders
    for date_dir in MESSAGES_PATH.iterdir():
        if date_dir.is_dir():
            for json_file in date_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_messages.extend(data)
                except Exception as e:
                    logger.error(f"Error reading {json_file}: {e}")
    
    logger.info(f"Ingested {len(all_messages)} messages.")
    return all_messages

def clean_data(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Clean the raw message data: remove duplicates, handle missing values, and type hint.
    """
    if not raw_data:
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)
    
    # 1. Remove duplicates based on channel_name and message_id
    initial_len = len(df)
    df = df.drop_duplicates(subset=['channel_name', 'message_id'], keep='first')
    logger.info(f"Removed {initial_len - len(df)} duplicate messages.")
    
    # 2. Handle missing values
    df['message_text'] = df['message_text'].fillna('')
    df['views'] = df['views'].fillna(0).astype(int)
    df['forwards'] = df['forwards'].fillna(0).astype(int)
    
    # 3. Filter out messages without text AND media (likely service messages)
    df = df[df['message_text'].str.strip().ne('') | df['has_media'] == True]
    
    # 4. Convert date to datetime
    df['message_date'] = pd.to_datetime(df['message_date'], errors='coerce')
    df = df.dropna(subset=['message_date'])
    
    logger.info(f"Cleaned data: {len(df)} records remaining.")
    return df

def load_to_db(df: pd.DataFrame) -> bool:
    """
    Load cleaned DataFrame into PostgreSQL.
    """
    if df.empty:
        logger.warning("No data to load into database.")
        return False

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info(f"Loading {len(df)} records into database...")
        
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO raw_telegram.telegram_messages 
                    (channel_name, message_id, message_text, message_date, 
                     views, forwards, media_path, raw_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (channel_name, message_id) DO NOTHING
                """, (
                    row['channel_name'],
                    row['message_id'],
                    row['message_text'],
                    row['message_date'],
                    row['views'],
                    row['forwards'],
                    row['image_path'],
                    json.dumps(row.to_dict(), default=str)
                ))
            except Exception as e:
                logger.error(f"Error inserting row {row['message_id']}: {e}")
                continue

        cursor.close()
        conn.close()
        logger.info("Database loading complete.")
        return True
        
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

if __name__ == "__main__":
    # Test script
    raw = ingest_data()
    cleaned = clean_data(raw)
    load_to_db(cleaned)
