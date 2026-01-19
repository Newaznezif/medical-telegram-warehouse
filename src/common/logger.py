"""
Logging utility for Medical Telegram Warehouse API
Updated for FastAPI integration
"""
import logging
import sys
from typing import Any
import structlog
from datetime import datetime
import json

from src.common.config import settings

def setup_logging():
    """
    Configure structured logging with structlog
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s" if settings.LOG_FORMAT == "json" else "%(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DEBUG else logging.WARNING
    )

def get_logger(name: str) -> Any:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name
        
    Returns:
        structlog logger instance
    """
    return structlog.get_logger(name)

class APIRequestLogger:
    """Logger for API requests and responses"""
    
    def __init__(self, name="api"):
        self.logger = get_logger(name)
    
    def log_request(self, request, request_body=None):
        """Log incoming request"""
        self.logger.info(
            "API Request",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_body=request_body,
        )
    
    def log_response(self, request, response, process_time_ms, response_body=None):
        """Log outgoing response"""
        self.logger.info(
            "API Response",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time_ms=process_time_ms,
            response_body=response_body,
        )
    
    def log_error(self, request, error):
        """Log API error"""
        self.logger.error(
            "API Error",
            method=request.method,
            path=request.url.path,
            error=str(error),
            error_type=type(error).__name__,
        )

# Example usage:
# logger = get_logger(__name__)
# logger.info("message", key="value", another_key=123)
# 
# request_logger = APIRequestLogger()
# request_logger.log_request(request)
