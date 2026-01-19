"""
API tests using pytest and HTTPX
"""
import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from datetime import datetime, date, timedelta
import json

from api.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "health" in data

def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data

def test_api_v1_health():
    """Test API v1 health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data

def test_generate_report():
    """Test report generation"""
    report_data = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-15",
        "time_range": "month",
        "include_details": True
    }
    
    response = client.post("/api/v1/reports/generate", json=report_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "summary" in data
    assert "channels" in data
    assert "top_objects" in data
    assert "time_series" in data
    assert "generated_at" in data
    
    # Check summary structure
    summary = data["summary"]
    assert "total_detections" in summary
    assert "avg_confidence" in summary

def test_list_channels():
    """Test channel listing"""
    response = client.get("/api/v1/channels")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    
    # Check at least one channel
    assert len(data["items"]) > 0
    
    # Check channel structure
    channel = data["items"][0]
    assert "id" in channel
    assert "name" in channel
    assert "category" in channel

def test_get_channel():
    """Test getting a specific channel"""
    response = client.get("/api/v1/channels/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "category" in data
    assert "detection_count" in data

def test_search_detections():
    """Test search functionality"""
    search_data = {
        "query": "medicine",
        "limit": 10,
        "offset": 0
    }
    
    response = client.post("/api/v1/search", json=search_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert "query" in data
    assert "search_time_ms" in data
    
    # Check result structure
    if data["results"]:
        result = data["results"][0]
        assert "image_path" in result
        assert "detected_class" in result
        assert "confidence" in result

def test_quick_search():
    """Test quick search with suggestions"""
    response = client.get("/api/v1/search/quick?q=med&limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert "query" in data
    assert "suggestions" in data
    assert "count" in data

def test_search_filters():
    """Test getting search filters"""
    response = client.get("/api/v1/search/filters")
    assert response.status_code == 200
    
    data = response.json()
    assert "channels" in data
    assert "objects" in data
    assert "confidence_ranges" in data
    assert "date_range" in data

def test_summary_report():
    """Test summary report endpoint"""
    response = client.get("/api/v1/reports/summary?days=30")
    assert response.status_code == 200
    
    data = response.json()
    assert "period_days" in data
    assert "total_detections" in data
    assert "avg_confidence" in data

def test_channel_report():
    """Test channel-specific report"""
    response = client.get("/api/v1/reports/channel/chemed_pharmacy?days=30")
    assert response.status_code == 200
    
    data = response.json()
    assert "channel_name" in data
    assert "detection_count" in data
    assert "avg_confidence" in data

def test_object_report():
    """Test object-specific report"""
    response = client.get("/api/v1/reports/object/bottle?days=30")
    assert response.status_code == 200
    
    data = response.json()
    assert "object_name" in data
    assert "detection_count" in data
    assert "avg_confidence" in data

def test_channel_stats():
    """Test channel statistics"""
    response = client.get("/api/v1/channels/chemed_pharmacy/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "channel" in data
    assert "total_detections" in data
    assert "avg_confidence" in data

def test_invalid_report_request():
    """Test report generation with invalid data"""
    invalid_data = {
        "start_date": "2024-01-15",
        "end_date": "2024-01-01",  # End date before start date
        "time_range": "invalid_range"
    }
    
    response = client.post("/api/v1/reports/generate", json=invalid_data)
    # Should return 422 for validation error
    assert response.status_code == 422

def test_nonexistent_channel():
    """Test getting non-existent channel"""
    response = client.get("/api/v1/channels/999")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_docs_endpoint():
    """Test Swagger UI docs"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_openapi_schema():
    """Test OpenAPI schema"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    
    # Check some expected endpoints
    assert "/api/v1/health" in data["paths"]
    assert "/api/v1/reports/generate" in data["paths"]
    assert "/api/v1/channels" in data["paths"]
    assert "/api/v1/search" in data["paths"]

# Skip async test for now since it requires mocking
# @pytest.mark.asyncio
# async def test_async_health_check():
#     """Test async health check"""
#     from api.routers.health import health_check
#     from unittest.mock import AsyncMock
    
#     # Mock database session
#     mock_db = AsyncMock()
#     mock_db.execute = AsyncMock(return_value=AsyncMock(scalar=lambda: 1))
    
#     response = await health_check(mock_db)
#     assert response.status == "healthy"
#     assert response.database is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
