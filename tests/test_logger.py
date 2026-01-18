"""
Tests for the logging utility
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import json
import logging
from src.common.logger import DetectionLogger, setup_logging, get_logger

class TestDetectionLogger:
    """Test DetectionLogger class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_logger_creation(self):
        """Test creating a logger"""
        logger = DetectionLogger(
            name="test_logger",
            log_dir=str(self.log_dir),
            level=logging.DEBUG,
            format_type="simple",
            console_output=False,
            file_output=True
        )
        
        assert logger.name == "test_logger"
        assert logger.logger.level == logging.DEBUG
        assert len(logger.logger.handlers) == 1  # Only file handler
        
        logger.close()
    
    def test_logger_with_json_format(self):
        """Test logger with JSON format"""
        logger = DetectionLogger(
            name="json_logger",
            log_dir=str(self.log_dir),
            level=logging.INFO,
            format_type="json",
            console_output=False,
            file_output=True
        )
        
        # Log a message with extra data
        logger.info("Test message", extra={"key1": "value1", "key2": 123})
        
        # Get log file
        log_file = logger.get_log_file_path()
        assert log_file is not None
        assert log_file.exists()
        
        # Read and parse log entry
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) >= 2  # Initialization + our message
            
            # Parse JSON log
            log_entry = json.loads(lines[-1])
            assert log_entry['message'] == "Test message"
            assert log_entry['level'] == "INFO"
            assert log_entry['key1'] == "value1"
            assert log_entry['key2'] == 123
        
        logger.close()
    
    def test_log_detection_method(self):
        """Test specialized detection logging"""
        logger = DetectionLogger(
            name="detection_logger",
            log_dir=str(self.log_dir),
            level=logging.INFO,
            format_type="detailed",
            console_output=False,
            file_output=True
        )
        
        logger.log_detection(
            image_path="/test/image.jpg",
            detected_class="bottle",
            confidence=0.85,
            channel="test_channel",
            x_center=0.5,
            y_center=0.5
        )
        
        log_file = logger.get_log_file_path()
        assert log_file is not None
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "bottle" in content
            assert "0.85" in content
            assert "test_channel" in content
        
        logger.close()
    
    def test_log_processing_methods(self):
        """Test processing start/end logging"""
        logger = DetectionLogger(
            name="processing_logger",
            log_dir=str(self.log_dir),
            level=logging.INFO,
            format_type="simple",
            console_output=False,
            file_output=True
        )
        
        logger.log_processing_start("test_task", total_items=100)
        logger.log_processing_end(
            "test_task",
            processed_items=95,
            success_count=90,
            error_count=5,
            duration_seconds=10.5
        )
        
        log_file = logger.get_log_file_path()
        assert log_file is not None
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Starting test_task" in content
            assert "Completed test_task" in content
            assert "Processed: 95" in content
            assert "Success: 90" in content
            assert "Errors: 5" in content
            assert "Duration: 10.50s" in content
        
        logger.close()
    
    def test_log_error_method(self):
        """Test error logging"""
        logger = DetectionLogger(
            name="error_logger",
            log_dir=str(self.log_dir),
            level=logging.ERROR,
            format_type="detailed",
            console_output=False,
            file_output=True
        )
        
        try:
            raise ValueError("Test error message")
        except Exception as e:
            logger.log_error(
                "test_error",
                "Something went wrong",
                exception=e,
                additional_info="test data"
            )
        
        log_file = logger.get_log_file_path()
        assert log_file is not None
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Error [test_error]" in content
            assert "Something went wrong" in content
            assert "ValueError" in content
            assert "Test error message" in content
        
        logger.close()
    
    def test_log_performance_method(self):
        """Test performance metric logging"""
        logger = DetectionLogger(
            name="performance_logger",
            log_dir=str(self.log_dir),
            level=logging.DEBUG,
            format_type="simple",
            console_output=False,
            file_output=True
        )
        
        logger.log_performance("inference_time", 0.045, unit="seconds")
        logger.log_performance("accuracy", 0.92)
        
        log_file = logger.get_log_file_path()
        assert log_file is not None
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "inference_time = 0.045 seconds" in content
            assert "accuracy = 0.92" in content
        
        logger.close()
    
    def test_log_level_changes(self):
        """Test changing log level"""
        logger = DetectionLogger(
            name="level_logger",
            log_dir=str(self.log_dir),
            level=logging.WARNING,
            console_output=False,
            file_output=True
        )
        
        # Debug message should not appear at WARNING level
        logger.debug("Debug message")
        
        log_file = logger.get_log_file_path()
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Debug message" not in content
        
        # Change to DEBUG level
        logger.set_level(logging.DEBUG)
        logger.debug("Debug message now")
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Debug message now" in content
        
        logger.close()
    
    def test_singleton_pattern(self):
        """Test that get_logger returns singleton"""
        logger1 = get_logger("singleton_test", log_dir=str(self.log_dir))
        logger2 = get_logger("singleton_test", log_dir=str(self.log_dir))
        
        assert logger1 is logger2
        
        # Different name should create new logger
        logger3 = get_logger("different_name", log_dir=str(self.log_dir))
        assert logger1 is not logger3
        
        logger1.close()
        logger3.close()
    
    def test_setup_logging_function(self):
        """Test setup_logging convenience function"""
        config = {
            'name': 'config_logger',
            'log_dir': str(self.log_dir),
            'level': logging.DEBUG,
            'format_type': 'json',
            'console_output': False,
            'file_output': True
        }
        
        logger = setup_logging(config)
        
        assert logger.name == 'config_logger'
        assert logger.logger.level == logging.DEBUG
        
        logger.info("Test from configured logger", test_key="test_value")
        
        log_file = logger.get_log_file_path()
        assert log_file is not None
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1])
            assert log_entry['message'] == "Test from configured logger"
            assert log_entry['test_key'] == "test_value"
        
        logger.close()

class TestConvenienceFunctions:
    """Test convenience logging functions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_quick_log_functions(self):
        """Test quick log functions"""
        # Setup global logger
        _ = setup_logging({
            'name': 'quick_logs',
            'log_dir': str(self.log_dir),
            'level': logging.DEBUG,
            'console_output': False,
            'file_output': True
        })
        
        # Use convenience functions
        log_debug("Debug message", extra_data="test")
        log_info("Info message", count=123)
        log_warning("Warning message")
        log_error("Error message")
        
        logger = get_logger()
        log_file = logger.get_log_file_path()
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Debug message" in content
            assert "Info message" in content
            assert "Warning message" in content
            assert "Error message" in content
        
        logger.close()
    
    def test_quick_detection_log(self):
        """Test quick detection log function"""
        _ = setup_logging({
            'name': 'quick_detection',
            'log_dir': str(self.log_dir),
            'level': logging.INFO,
            'console_output': False,
            'file_output': True
        })
        
        log_detection(
            image_path="/test/image.jpg",
            detected_class="medicine",
            confidence=0.88,
            channel="medical"
        )
        
        logger = get_logger()
        log_file = logger.get_log_file_path()
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "medicine" in content
            assert "0.88" in content
            assert "medical" in content
        
        logger.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
