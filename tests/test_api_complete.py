import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Telegram Medical Warehouse API"
    assert "endpoints" in data

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_get_channels():
    """Test channels endpoint"""
    response = client.get("/api/v1/channels")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "channels" in data
    assert len(data["channels"]) > 0

def test_get_detections():
    """Test detections endpoint with parameters"""
    response = client.get("/api/v1/detections?limit=5&min_confidence=0.7")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "detections" in data
    assert data["limit"] == 5
    assert data["min_confidence"] == 0.7

def test_get_detection_stats():
    """Test detection statistics endpoint"""
    response = client.get("/api/v1/detections/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "stats" in data
    assert "total_detections" in data["stats"]

def test_get_messages():
    """Test messages endpoint"""
    response = client.get("/api/v1/messages?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "messages" in data

def test_search():
    """Test search endpoint"""
    response = client.get("/api/v1/search?q=medicine")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["query"] == "medicine"

def test_invalid_parameters():
    """Test error handling for invalid parameters"""
    response = client.get("/api/v1/detections?min_confidence=invalid")
    assert response.status_code == 422  # Validation error

def test_not_found_endpoint():
    """Test 404 for non-existent endpoint"""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
