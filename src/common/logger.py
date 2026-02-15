"""
Logging configuration for the pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages toward Loguru."""
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(
    name: str = "medical_telegram",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "500 MB",
    retention: str = "30 days",
    enqueue: bool = True,
) -> logger:
    """
    Setup Loguru logger with configuration.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs only to console)
        rotation: Log rotation size or time
        retention: Log retention period
    
    Returns:
        Configured logger instance
    """
    
    # Remove default handler
    logger.remove()
    
    # Console output format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # File output format (includes more details)
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "pid={process} | "
        "tid={thread} | "
        "{message} | "
        "{extra}"
    )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            str(log_path),
            format=file_format,
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=enqueue,  # Async logging if True
        )
    
    # Also add error log file
    error_log = Path("logs/errors.log")
    error_log.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(error_log),
        format=file_format,
        level="ERROR",
        rotation="100 MB",
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    return logger.bind(pipeline="medical_telegram")


def log_pipeline_start(pipeline_name: str, run_id: str, config: dict) -> None:
    """Log pipeline start with configuration."""
    
    logger.info(f"🚀 Starting pipeline: {pipeline_name}")
    logger.info(f"📝 Run ID: {run_id}")
    logger.info(f"⚙️  Configuration: {json.dumps(config, indent=2, default=str)}")
    logger.info(f"📁 Working directory: {Path.cwd()}")


def log_pipeline_end(pipeline_name: str, run_id: str, duration: float, status: str) -> None:
    """Log pipeline completion."""
    
    if status == "success":
        logger.success(f"✅ Pipeline completed: {pipeline_name}")
    else:
        logger.error(f"❌ Pipeline failed: {pipeline_name}")
    
    logger.info(f"📝 Run ID: {run_id}")
    logger.info(f"⏱️  Duration: {duration:.2f} seconds")
    logger.info(f"📊 Status: {status}")


def log_task_start(task_name: str, task_id: str) -> None:
    """Log task start."""
    logger.info(f"▶️  Starting task: {task_name} (ID: {task_id})")


def log_task_end(task_name: str, task_id: str, duration: float, success: bool) -> None:
    """Log task completion."""
    
    if success:
        logger.success(f"✓ Task completed: {task_name}")
    else:
        logger.error(f"✗ Task failed: {task_name}")
    
    logger.info(f"   ID: {task_id}")
    logger.info(f"   Duration: {duration:.2f} seconds")


def log_detection_results(detections: list, model: str, confidence_threshold: float) -> None:
    """Log YOLO detection results."""
    
    if not detections:
        logger.warning(f"No detections found with model: {model}")
        return
    
    # Count by class
    class_counts = {}
    for detection in detections:
        class_name = detection.get("class", "unknown")
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    logger.info(f"🔍 Detection Results:")
    logger.info(f"   Model: {model}")
    logger.info(f"   Confidence threshold: {confidence_threshold}")
    logger.info(f"   Total detections: {len(detections)}")
    
    for class_name, count in class_counts.items():
        logger.info(f"   - {class_name}: {count}")
    
    # Log high confidence detections
    high_conf = [d for d in detections if d.get("confidence", 0) > 0.8]
    if high_conf:
        logger.info(f"   High confidence (>0.8): {len(high_conf)}")


def log_database_stats(engine, table_name: str) -> None:
    """Log database table statistics."""
    
    try:
        with engine.connect() as conn:
            # Get row count
            count_result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = count_result.scalar()
            
            # Get latest timestamp
            time_result = conn.execute(
                f"SELECT MAX(created_at) FROM {table_name}"
            )
            latest_time = time_result.scalar()
            
            logger.info(f"📊 Database Stats for {table_name}:")
            logger.info(f"   Total rows: {row_count:,}")
            logger.info(f"   Latest entry: {latest_time}")
            
    except Exception as e:
        logger.error(f"Failed to get database stats: {str(e)}")


def log_api_health(api_url: str, response_time: float, status_code: int) -> None:
    """Log API health check results."""
    
    if 200 <= status_code < 300:
        logger.success(f"🌐 API Health: {api_url}")
    else:
        logger.error(f"🌐 API Health Check Failed: {api_url}")
    
    logger.info(f"   Status Code: {status_code}")
    logger.info(f"   Response Time: {response_time:.2f} seconds")


def log_system_metrics() -> None:
    """Log current system metrics."""
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(".")
    
    logger.info("📈 System Metrics:")
    logger.info(f"   CPU Usage: {cpu_percent}%")
    logger.info(f"   Memory Usage: {memory.percent}% ({memory.used / (1024**3):.1f} GB used)")
    logger.info(f"   Disk Usage: {disk.percent}% ({disk.used / (1024**3):.1f} GB used)")
    
    # Log warning if usage is high
    if cpu_percent > 80:
        logger.warning("⚠️  High CPU usage detected")
    if memory.percent > 80:
        logger.warning("⚠️  High memory usage detected")
    if disk.percent > 90:
        logger.warning("⚠️  High disk usage detected")


def log_error_with_context(error: Exception, context: dict = None) -> None:
    """Log error with context information."""
    
    logger.error(f"💥 Error occurred: {type(error).__name__}")
    logger.error(f"   Message: {str(error)}")
    
    if context:
        logger.error("   Context:")
        for key, value in context.items():
            logger.error(f"     {key}: {value}")
    
    import traceback
    logger.error(f"   Traceback:\n{traceback.format_exc()}")


# Global logger instance
log = setup_logger()


if __name__ == "__main__":
    # Test the logger
    log.info("Logger configured successfully")
    log.warning("This is a warning message")
    log.error("This is an error message")
    
    # Test structured logging
    log.info("Structured log", extra={
        "user": "admin",
        "action": "test",
        "timestamp": datetime.now().isoformat()
    })
