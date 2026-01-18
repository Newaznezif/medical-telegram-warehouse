"""
Logging utility for medical warehouse detection system
Provides structured logging with different levels, file rotation, and console output
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
import json
from typing import Optional, Dict, Any
import inspect

class DetectionLogger:
    """Custom logger for YOLO detection system"""
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    # Log formats
    SIMPLE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    JSON_FORMAT = 'json'
    
    def __init__(self, 
                 name: str = 'detection',
                 log_dir: Optional[str] = None,
                 level: int = logging.INFO,
                 format_type: str = 'detailed',
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 console_output: bool = True,
                 file_output: bool = True):
        """
        Initialize the logger
        
        Args:
            name: Logger name
            log_dir: Directory for log files (default: logs/)
            level: Logging level
            format_type: 'simple', 'detailed', or 'json'
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
            console_output: Enable console output
            file_output: Enable file output
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Set log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path('logs')
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure formatter
        if format_type == 'simple':
            formatter = logging.Formatter(self.SIMPLE_FORMAT)
            self.json_format = False
        elif format_type == 'detailed':
            formatter = logging.Formatter(self.DETAILED_FORMAT)
            self.json_format = False
        elif format_type == 'json':
            formatter = JsonFormatter()
            self.json_format = True
        else:
            formatter = logging.Formatter(self.DETAILED_FORMAT)
            self.json_format = False
        
        # Add console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler
        if file_output:
            # Create log file name with timestamp
            timestamp = datetime.now().strftime('%Y%m%d')
            log_file = self.log_dir / f'{name}_{timestamp}.log'
            
            # Use rotating file handler
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Store metadata
        self.metadata = {
            'logger_name': name,
            'start_time': datetime.now().isoformat(),
            'log_level': logging.getLevelName(level),
            'format_type': format_type
        }
        
        self.logger.info(f"Logger initialized: {name} (level: {logging.getLevelName(level)})")
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, extra, **kwargs)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, extra, **kwargs)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, extra, **kwargs)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, message, extra, **kwargs)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, message, extra, **kwargs)
    
    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Internal logging method with caller information
        
        Args:
            level: Log level
            message: Log message
            extra: Additional metadata
            **kwargs: Additional key-value pairs for JSON logging
        """
        if extra is None:
            extra = {}
        
        # Add caller information
        if not self.json_format:
            frame = inspect.currentframe().f_back.f_back
            caller_info = inspect.getframeinfo(frame)
            extra['caller_file'] = caller_info.filename
            extra['caller_line'] = caller_info.lineno
            extra['caller_function'] = caller_info.function
        
        # Merge extra and kwargs
        all_extra = {**extra, **kwargs}
        
        if all_extra:
            self.logger.log(level, message, extra=all_extra)
        else:
            self.logger.log(level, message)
    
    def log_detection(self, 
                     image_path: str,
                     detected_class: str,
                     confidence: float,
                     channel: Optional[str] = None,
                     timestamp: Optional[str] = None,
                     **kwargs):
        """
        Log a detection event
        
        Args:
            image_path: Path to the detected image
            detected_class: Detected object class
            confidence: Detection confidence score
            channel: Channel/source of the image
            timestamp: Detection timestamp
            **kwargs: Additional detection metadata
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        log_data = {
            'event': 'detection',
            'timestamp': timestamp,
            'image_path': str(image_path),
            'detected_class': detected_class,
            'confidence': confidence,
            'channel': channel,
            **kwargs
        }
        
        self.info(f"Detection: {detected_class} ({confidence:.3f}) in {image_path}", **log_data)
    
    def log_processing_start(self, 
                           task: str,
                           total_items: Optional[int] = None,
                           **kwargs):
        """
        Log start of a processing task
        
        Args:
            task: Task name/description
            total_items: Total number of items to process
            **kwargs: Additional task metadata
        """
        log_data = {
            'event': 'processing_start',
            'task': task,
            'total_items': total_items,
            'start_time': datetime.now().isoformat(),
            **kwargs
        }
        
        if total_items:
            self.info(f"Starting {task} ({total_items} items)", **log_data)
        else:
            self.info(f"Starting {task}", **log_data)
    
    def log_processing_end(self,
                         task: str,
                         processed_items: Optional[int] = None,
                         success_count: Optional[int] = None,
                         error_count: Optional[int] = None,
                         duration_seconds: Optional[float] = None,
                         **kwargs):
        """
        Log end of a processing task
        
        Args:
            task: Task name/description
            processed_items: Number of items processed
            success_count: Number of successful items
            error_count: Number of errors
            duration_seconds: Processing duration in seconds
            **kwargs: Additional task metadata
        """
        log_data = {
            'event': 'processing_end',
            'task': task,
            'processed_items': processed_items,
            'success_count': success_count,
            'error_count': error_count,
            'duration_seconds': duration_seconds,
            'end_time': datetime.now().isoformat(),
            **kwargs
        }
        
        message = f"Completed {task}"
        if processed_items is not None:
            message += f" - Processed: {processed_items}"
        if success_count is not None:
            message += f", Success: {success_count}"
        if error_count is not None:
            message += f", Errors: {error_count}"
        if duration_seconds is not None:
            message += f", Duration: {duration_seconds:.2f}s"
        
        self.info(message, **log_data)
    
    def log_error(self,
                 error_type: str,
                 message: str,
                 exception: Optional[Exception] = None,
                 **kwargs):
        """
        Log an error
        
        Args:
            error_type: Type of error
            message: Error message
            exception: Exception object (if any)
            **kwargs: Additional error metadata
        """
        log_data = {
            'event': 'error',
            'error_type': error_type,
            'error_message': message,
            'exception_type': type(exception).__name__ if exception else None,
            'exception_details': str(exception) if exception else None,
            **kwargs
        }
        
        self.error(f"Error [{error_type}]: {message}", **log_data)
    
    def log_performance(self,
                       metric_name: str,
                       value: float,
                       unit: Optional[str] = None,
                       **kwargs):
        """
        Log performance metric
        
        Args:
            metric_name: Name of the performance metric
            value: Metric value
            unit: Unit of measurement
            **kwargs: Additional metadata
        """
        log_data = {
            'event': 'performance',
            'metric': metric_name,
            'value': value,
            'unit': unit,
            **kwargs
        }
        
        if unit:
            self.debug(f"Performance: {metric_name} = {value} {unit}", **log_data)
        else:
            self.debug(f"Performance: {metric_name} = {value}", **log_data)
    
    def get_log_file_path(self) -> Optional[Path]:
        """Get current log file path"""
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                return Path(handler.baseFilename)
        return None
    
    def set_level(self, level: int):
        """Set logging level"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)
        self.info(f"Log level changed to {logging.getLevelName(level)}")
    
    def close(self):
        """Close all handlers and cleanup"""
        for handler in self.logger.handlers:
            handler.close()
        self.logger.info("Logger closed")

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            'timestamp': self.formatTime(record),
            'logger': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'event'):
            log_entry['event'] = record.event
        
        # Add all extra attributes
        for key, value in record.__dict__.items():
            if key.startswith('_') or key in ['args', 'asctime', 'created', 'exc_info', 
                                            'exc_text', 'filename', 'funcName', 'levelname',
                                            'levelno', 'lineno', 'module', 'msecs', 'message',
                                            'msg', 'name', 'pathname', 'process', 'processName',
                                            'relativeCreated', 'stack_info', 'thread', 'threadName']:
                continue
            if key not in log_entry and value is not None:
                log_entry[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

# Global logger instance
_default_logger = None

def get_logger(name: str = 'detection', **kwargs) -> DetectionLogger:
    """
    Get or create a logger instance (singleton pattern)
    
    Args:
        name: Logger name
        **kwargs: Additional logger configuration
        
    Returns:
        DetectionLogger instance
    """
    global _default_logger
    
    if _default_logger is None or _default_logger.name != name:
        _default_logger = DetectionLogger(name, **kwargs)
    
    return _default_logger

def setup_logging(config: Optional[Dict[str, Any]] = None) -> DetectionLogger:
    """
    Setup logging with configuration
    
    Args:
        config: Logger configuration dictionary
        
    Returns:
        Configured DetectionLogger instance
    """
    default_config = {
        'name': 'detection',
        'log_dir': 'logs',
        'level': logging.INFO,
        'format_type': 'detailed',
        'console_output': True,
        'file_output': True,
        'max_bytes': 10 * 1024 * 1024,
        'backup_count': 5
    }
    
    if config:
        default_config.update(config)
    
    return get_logger(**default_config)

# Convenience functions for quick logging
def log_debug(message: str, **kwargs):
    """Quick debug log"""
    logger = get_logger()
    logger.debug(message, **kwargs)

def log_info(message: str, **kwargs):
    """Quick info log"""
    logger = get_logger()
    logger.info(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Quick warning log"""
    logger = get_logger()
    logger.warning(message, **kwargs)

def log_error(message: str, **kwargs):
    """Quick error log"""
    logger = get_logger()
    logger.error(message, **kwargs)

def log_critical(message: str, **kwargs):
    """Quick critical log"""
    logger = get_logger()
    logger.critical(message, **kwargs)

def log_detection(image_path: str, detected_class: str, confidence: float, **kwargs):
    """Quick detection log"""
    logger = get_logger()
    logger.log_detection(image_path, detected_class, confidence, **kwargs)

if __name__ == "__main__":
    # Example usage
    logger = setup_logging({
        'name': 'test_logger',
        'level': logging.DEBUG,
        'format_type': 'json'
    })
    
    logger.info("Starting detection system")
    logger.log_processing_start("YOLO detection", total_items=100)
    
    # Simulate some detections
    logger.log_detection(
        image_path="/path/to/image1.jpg",
        detected_class="bottle",
        confidence=0.85,
        channel="medical_channel",
        x_center=0.5,
        y_center=0.5
    )
    
    logger.log_detection(
        image_path="/path/to/image2.jpg",
        detected_class="medicine",
        confidence=0.92,
        channel="cosmetic_channel",
        x_center=0.6,
        y_center=0.4
    )
    
    logger.log_performance("inference_time", 0.045, unit="seconds")
    logger.log_performance("memory_usage", 512.5, unit="MB")
    
    logger.log_processing_end(
        "YOLO detection",
        processed_items=100,
        success_count=95,
        error_count=5,
        duration_seconds=45.2
    )
    
    try:
        # Simulate an error
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.log_error("processing_error", "Failed to process image", exception=e)
    
    logger.info("Detection system stopped")
    logger.close()
