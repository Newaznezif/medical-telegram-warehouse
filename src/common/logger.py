import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from src.common.config import config


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
            
        return json.dumps(log_record)


def setup_logger(
    name: str = "medical_telegram",
    log_level: str = "INFO",
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    log_format: str = "json"  # "json" or "text"
) -> logging.Logger:
    """
    Setup and return a configured logger instance
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Whether to log to file
        enable_console_logging: Whether to log to console
        log_format: Output format ("json" for structured logging, "text" for human-readable)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path(config.LOG_PATH)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    if log_format.lower() == "json":
        file_formatter = JSONFormatter()
        console_formatter = JSONFormatter()
    else:
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
    
    # File handler (rotating logs)
    if enable_file_logging:
        from logging.handlers import RotatingFileHandler
        
        # Main log file
        main_handler = RotatingFileHandler(
            filename=log_dir / 'pipeline.log',
            maxBytes=10_485_760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(level)
        main_handler.setFormatter(file_formatter)
        logger.addHandler(main_handler)
        
        # Error log file (only ERROR and above)
        error_handler = RotatingFileHandler(
            filename=log_dir / 'errors.log',
            maxBytes=5_242_880,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
    
    # Console handler
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_task_logger(task_name: str, **kwargs) -> logging.Logger:
    """
    Get a logger for a specific task with task context
    
    Args:
        task_name: Name of the task (e.g., "scraping", "yolo_detection")
        **kwargs: Additional context to add to logs
    
    Returns:
        logging.Logger: Task-specific logger
    """
    logger = setup_logger(f"medical_telegram.{task_name}", **kwargs)
    
    # Add task context to log records
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.task = task_name
        record.extra = kwargs
        return record
    
    logging.setLogRecordFactory(record_factory)
    
    return logger


# Create default logger instances
logger = setup_logger()

# Convenience functions for common logging patterns
def log_scraping_start(channel: str, limit: int):
    """Log the start of a scraping operation"""
    logger.info(
        f"Starting to scrape channel: {channel}",
        extra={
            "channel": channel,
            "limit": limit,
            "action": "scraping_start"
        }
    )


def log_scraping_complete(channel: str, message_count: int, duration: float):
    """Log the completion of a scraping operation"""
    logger.info(
        f"Completed scraping {message_count} messages from {channel}",
        extra={
            "channel": channel,
            "message_count": message_count,
            "duration_seconds": duration,
            "action": "scraping_complete"
        }
    )


def log_error_with_context(error: Exception, context: Dict[str, Any]):
    """Log an error with additional context"""
    logger.error(
        f"Error: {str(error)}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            **context,
            "action": "error"
        },
        exc_info=True
    )


def log_pipeline_step(step_name: str, status: str, details: Optional[Dict] = None):
    """Log a pipeline step with status"""
    log_data = {
        "step": step_name,
        "status": status,
        "action": "pipeline_step"
    }
    
    if details:
        log_data.update(details)
    
    if status.lower() == "error":
        logger.error(f"Pipeline step '{step_name}' failed", extra=log_data)
    elif status.lower() == "warning":
        logger.warning(f"Pipeline step '{step_name}' warning", extra=log_data)
    else:
        logger.info(f"Pipeline step '{step_name}' completed", extra=log_data)


# Export common logging functions
__all__ = [
    'logger',
    'setup_logger',
    'get_task_logger',
    'log_scraping_start',
    'log_scraping_complete',
    'log_error_with_context',
    'log_pipeline_step'
]