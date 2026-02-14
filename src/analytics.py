import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

from src.config import ANOMALY_CONFIDENCE_THRESHOLD, RISK_SCORE_THRESHOLD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate key performance indicators from the message data.
    """
    if df.empty:
        logger.warning("Empty DataFrame provided for KPI calculations.")
        return {}

    kpis = {
        "total_messages": len(df),
        "total_views": int(df["views"].sum()),
        "avg_views_per_message": float(df["views"].mean()),
        "total_forwards": int(df["forwards"].sum()),
        "channels_count": int(df["channel_name"].nunique()),
        "messages_per_channel": df["channel_name"].value_counts().to_dict(),
        "total_media_messages": int(df["has_media"].sum())
    }
    
    logger.info(f"Calculated KPIs for {len(df)} messages.")
    return kpis

def get_risk_scores(df: pd.DataFrame) -> pd.Series:
    """
    Calculate a simple risk/anomaly score for messages based on engagement metrics.
    Produces numeric output as requested.
    """
    if df.empty:
        return pd.Series(dtype=float)

    # Simplified risk score: (views * 0.7 + forwards * 0.3) normalized
    # In a real scenario, this would use a more sophisticated model
    
    # Avoid division by zero
    max_engagement = df["views"].max() + df["forwards"].max()
    if max_engagement == 0:
        return pd.Series(0.0, index=df.index)
        
    risk_scores = (df["views"] * 0.1 + df["forwards"] * 2.0) / (max_engagement + 1)
    
    # Clip to 0-1 range
    risk_scores = risk_scores.clip(0, 1)
    
    logger.info("Generated risk scores for messages.")
    return risk_scores

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag messages as anomalies based on risk scores and threshold.
    """
    if df.empty:
        return df

    df = df.copy()
    df["risk_score"] = get_risk_scores(df)
    df["is_anomaly"] = df["risk_score"] > RISK_SCORE_THRESHOLD
    
    anomaly_count = df["is_anomaly"].sum()
    logger.info(f"Detected {anomaly_count} anomalies.")
    
    return df

if __name__ == "__main__":
    # Test sample
    data = {
        "channel_name": ["C1", "C2", "C1"],
        "views": [100, 5000, 150],
        "forwards": [5, 100, 10],
        "has_media": [True, True, False]
    }
    test_df = pd.DataFrame(data)
    print(calculate_kpis(test_df))
    print(detect_anomalies(test_df))
