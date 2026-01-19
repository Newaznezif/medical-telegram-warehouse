"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import time
import psutil
import os

from api.database import get_db
from api.schemas import HealthResponse
from src.common.config import settings
from src.common.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Application start time
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    Returns API health status and database connectivity
    """
    # Check database
    db_healthy = False
    try:
        result = await db.execute(text("SELECT 1"))
        db_healthy = result.scalar() == 1
    except Exception as e:
        logger.warning("Database health check failed", error=str(e))
    
    # Get system info
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    
    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        database=db_healthy,
        memory_usage_mb=memory_usage,
        uptime_seconds=time.time() - START_TIME,
    )

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check with system information
    """
    # Database check
    db_healthy = False
    db_version = "unknown"
    try:
        result = await db.execute(text("SELECT version()"))
        db_version = result.scalar()
        db_healthy = True
    except Exception as e:
        db_version = f"error: {str(e)}"
    
    # System info
    import platform
    process = psutil.Process(os.getpid())
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "application": {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime_seconds": time.time() - START_TIME,
        },
        "database": {
            "healthy": db_healthy,
            "version": db_version,
        },
        "system": {
            "platform": platform.system(),
            "release": platform.release(),
            "python_version": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
        },
        "process": {
            "pid": process.pid,
            "name": process.name(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
        },
    }

@router.get("/health/ping")
async def ping():
    """
    Simple ping endpoint
    """
    return {"ping": "pong", "timestamp": datetime.utcnow().isoformat()}
