import logging
import sys
import os
from pathlib import Path
from typing import Optional

# Add project root to sys.path for direct execution
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.etl import ingest_data, clean_data, load_to_db
from src.analytics import calculate_kpis, detect_anomalies

from src.common.logger import setup_logger, log_pipeline_start, log_pipeline_end

# Configure logging
logger = setup_logger("MedicalPipeline")

def run_pipeline() -> Optional[bool]:
    """
    Main orchestration function for the Medical Telegram Warehouse ETL pipeline.
    """
    logger.info("Starting Medical Telegram Warehouse Pipeline...")
    
    try:
        # 1. Ingestion
        raw_messages = ingest_data()
        if not raw_messages:
            logger.warning("No data ingested. Exiting.")
            return False
            
        # 2. Cleaning
        cleaned_df = clean_data(raw_messages)
        if cleaned_df.empty:
            logger.warning("No data remaining after cleaning. Exiting.")
            return False
            
        # 3. Analytics & KPI Calculations
        kpis = calculate_kpis(cleaned_df)
        logger.info(f"Pipeline KPIs: {kpis}")
        
        # 4. Anomaly Detection
        analyzed_df = detect_anomalies(cleaned_df)
        
        # 5. Database Loading
        success = load_to_db(analyzed_df)
        if success:
            logger.info("Pipeline execution completed successfully.")
        else:
            logger.error("Pipeline failed during database loading.")
            
        return success

    except Exception as e:
        logger.error(f"Pipeline crashed with error: {e}")
        return False

if __name__ == "__main__":
    run_pipeline()
