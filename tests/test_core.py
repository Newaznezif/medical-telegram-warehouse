import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
import os
import json

from src.etl import ingest_data, clean_data, load_to_db
from src.analytics import calculate_kpis, get_risk_scores, detect_anomalies

# Test Data
MOCK_RAW_DATA = [
    {
        "channel_name": "@CheMed123",
        "message_id": 1,
        "message_date": "2024-01-01T12:00:00",
        "message_text": "Sample text 1",
        "views": 100,
        "forwards": 10,
        "has_media": True,
        "image_path": "path/1.jpg"
    },
    {
        "channel_name": "@CheMed123",
        "message_id": 1,  # Duplicate ID
        "message_date": "2024-01-01T12:00:00",
        "message_text": "Sample text 1",
        "views": 100,
        "forwards": 10,
        "has_media": True,
        "image_path": "path/1.jpg"
    },
    {
        "channel_name": "@lobelia4cosmetics",
        "message_id": 2,
        "message_date": "2024-01-02T12:00:00",
        "message_text": "Sample text 2",
        "views": 500,
        "forwards": 50,
        "has_media": False,
        "image_path": None
    }
]

def test_ingest_data_returns_valid_list():
    """Test 1: Data ingestion returns a valid list of messages"""
    with patch("src.etl.MESSAGES_PATH") as mock_path:
        mock_path.exists.return_value = True
        mock_path.iterdir.return_value = [] # Empty for simplicity or mock files
        result = ingest_data()
        assert isinstance(result, list)

def test_clean_data_removes_duplicates():
    """Test 2: Cleaning function removes duplicate messages"""
    df = clean_data(MOCK_RAW_DATA)
    # 3 items in MOCK_RAW_DATA, 1 is duplicate
    assert len(df) == 2
    assert df["message_id"].is_unique

def test_calculate_kpis_produces_correct_values():
    """Test 3: Aggregation function produces correct KPI values"""
    df = clean_data(MOCK_RAW_DATA)
    kpis = calculate_kpis(df)
    assert kpis["total_messages"] == 2
    assert kpis["total_views"] == 600
    assert kpis["avg_views_per_message"] == 300.0

def test_risk_scoring_produces_numeric_output():
    """Test 4: Risk scoring produces numeric output between 0 and 1"""
    df = clean_data(MOCK_RAW_DATA)
    scores = get_risk_scores(df)
    assert isinstance(scores, pd.Series)
    assert scores.dtype == float
    assert all(0 <= s <= 1 for s in scores)

def test_detect_anomalies_flags_correctly():
    """Test 5: Anomaly detection flags messages correctly based on risk scores"""
    df = clean_data(MOCK_RAW_DATA)
    analyzed_df = detect_anomalies(df)
    assert "risk_score" in analyzed_df.columns
    assert "is_anomaly" in analyzed_df.columns
    assert analyzed_df["is_anomaly"].dtype == bool

def test_clean_data_edge_cases():
    """Test 6: cleaning function handles missing values and invalid dates"""
    edge_case_data = [
        {
            "channel_name": "@EdgeCase",
            "message_id": 100,
            "message_date": "invalid-date",
            "message_text": None,
            "views": None,
            "forwards": None,
            "has_media": False,
            "image_path": None
        }
    ]
    df = clean_data(edge_case_data)
    # Invalid date should be dropped by current implementation
    assert len(df) == 0

def test_calculate_kpis_handles_empty_df():
    """Test 7: KPI calculation handles empty DataFrame gracefully"""
    df = pd.DataFrame()
    kpis = calculate_kpis(df)
    assert kpis == {}

@patch("psycopg2.connect")
def test_load_to_db_success(mock_connect):
    """Test 8: Database insertions are handled successfully (mocked)"""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    
    df = clean_data(MOCK_RAW_DATA)
    success = load_to_db(df)
    
    assert success is True
    assert mock_conn.cursor.called
