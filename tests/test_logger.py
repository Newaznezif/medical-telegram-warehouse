"""
Tests for the loguru-based logging utility in src/common/logger.py
"""
import pytest
import os
import json
from pathlib import Path
from src.common.logger import (
    setup_logger, 
    log_pipeline_start, 
    log_pipeline_end, 
    log_task_start, 
    log_task_end,
    log_detection_results,
    log_error_with_context
)

@pytest.fixture
def temp_log_file(tmp_path):
    log_file = tmp_path / "test_pipeline.log"
    return str(log_file)

def test_setup_logger(temp_log_file):
    """Test that setup_logger creates a logger that can write to a file."""
    logger = setup_logger(name="test_logger", log_file=temp_log_file, enqueue=False)
    logger.info("Test message")
    
    assert os.path.exists(temp_log_file)
    with open(temp_log_file, "r") as f:
        content = f.read()
        assert "test_logger" in content
        assert "Test message" in content

def test_log_pipeline_start_end(temp_log_file, caplog):
    """Test pipeline start and end logging."""
    # We use setup_logger with a file to verify file output as well
    setup_logger(log_file=temp_log_file, enqueue=False)
    
    log_pipeline_start("TestPipeline", "run_123", {"param": "value"})
    log_pipeline_end("TestPipeline", "run_123", 10.5, "success")
    
    assert os.path.exists(temp_log_file)
    with open(temp_log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Starting pipeline: TestPipeline" in content
        assert "run_123" in content
        assert "Pipeline completed: TestPipeline" in content
        assert "10.50 seconds" in content

def test_log_task_start_end(temp_log_file):
    """Test task start and end logging."""
    setup_logger(log_file=temp_log_file, enqueue=False)
    
    log_task_start("TestTask", "task_456")
    log_task_end("TestTask", "task_456", 5.2, True)
    
    with open(temp_log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Starting task: TestTask" in content
        assert "task_456" in content
        assert "Task completed: TestTask" in content

def test_log_detection_results(temp_log_file):
    """Test logging of YOLO detection results."""
    setup_logger(log_file=temp_log_file, enqueue=False)
    
    detections = [
        {"class": "medicine", "confidence": 0.9},
        {"class": "medicine", "confidence": 0.85},
        {"class": "bottle", "confidence": 0.7}
    ]
    
    log_detection_results(detections, "yolov8n", 0.5)
    
    with open(temp_log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Detection Results" in content
        assert "medicine: 2" in content
        assert "bottle: 1" in content
        assert "High confidence (>0.8): 2" in content

def test_log_error_with_context(temp_log_file):
    """Test error logging with context."""
    setup_logger(log_file=temp_log_file, enqueue=False)
    
    try:
        raise ValueError("Something went wrong")
    except Exception as e:
        log_error_with_context(e, {"step": "ingestion", "id": "msg_001"})
    
    with open(temp_log_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Error occurred: ValueError" in content
        assert "Something went wrong" in content
        assert "step: ingestion" in content
        assert "id: msg_001" in content
        assert "Traceback" in content
