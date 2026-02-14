from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple settings
class Settings:
    PROJECT_NAME = "Telegram Medical Warehouse API"
    VERSION = "1.0.0"
    DEBUG = True
    BACKEND_CORS_ORIGINS = ["*"]
    
    # Database from environment or defaults
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "medical_warehouse")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info("=" * 60)
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    yield
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "timestamp": time.time(),
        "endpoints": {
            "health": "/health",
            "channels": "/api/v1/channels",
            "detections": "/api/v1/detections",
            "messages": "/api/v1/messages",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "postgresql (configured)",
        "timestamp": time.time()
    }

@app.get("/api/v1/channels")
async def get_channels():
    """Get all Telegram channels"""
    # Mock data - will be replaced with database
    channels = [
        {
            "channel_key": "chemed123",
            "channel_name": "chemed123",
            "description": "Medical equipment and pharmaceutical postings",
            "total_messages": 450,
            "total_views": 12500,
            "total_forwards": 320
        },
        {
            "channel_key": "lobelia4cosmetics",
            "channel_name": "lobelia4cosmetics",
            "description": "Cosmetics and health-related products",
            "total_messages": 380,
            "total_views": 9800,
            "total_forwards": 210
        },
        {
            "channel_key": "tikvahpharma",
            "channel_name": "tikvahpharma",
            "description": "Pharmaceutical distribution announcements",
            "total_messages": 241,
            "total_views": 7200,
            "total_forwards": 150
        }
    ]
    return {
        "success": True,
        "count": len(channels),
        "channels": channels
    }

@app.get("/api/v1/detections")
async def get_detections(
    limit: int = 50,
    min_confidence: float = 0.5,
    channel: str = None
):
    """Get YOLO detection results"""
    # Mock data - will be replaced with database
    detections = []
    
    sample_classes = ["medicine", "cosmetic", "bottle", "box", "package", "syringe", "pill", "cream"]
    sample_channels = ["chemed123", "lobelia4cosmetics", "tikvahpharma"]
    
    for i in range(min(limit, 20)):
        channel_name = channel if channel else sample_channels[i % len(sample_channels)]
        detections.append({
            "detection_id": f"det_{i:04d}",
            "image_name": f"image_{i:03d}.jpg",
            "channel_name": channel_name,
            "detected_class": sample_classes[i % len(sample_classes)],
            "confidence": round(0.5 + (i * 0.02), 2),
            "product_category": "medical" if i % 3 == 0 else "cosmetic",
            "date_str": "2024-01-15",
            "processed_at": "2024-01-15T10:30:00"
        })
    
    # Filter by confidence
    detections = [d for d in detections if d["confidence"] >= min_confidence]
    
    # Filter by channel if specified
    if channel:
        detections = [d for d in detections if d["channel_name"] == channel]
    
    return {
        "success": True,
        "count": len(detections),
        "limit": limit,
        "min_confidence": min_confidence,
        "channel_filter": channel,
        "detections": detections[:limit]
    }

@app.get("/api/v1/detections/stats")
async def get_detection_stats():
    """Get detection statistics"""
    return {
        "success": True,
        "stats": {
            "total_detections": 1071,
            "unique_classes": 15,
            "unique_channels": 3,
            "avg_confidence": 0.78,
            "top_classes": [
                {"class": "medicine", "count": 245},
                {"class": "bottle", "count": 198},
                {"class": "cosmetic", "count": 187},
                {"class": "box", "count": 156},
                {"class": "package", "count": 132}
            ],
            "channel_distribution": [
                {"channel": "chemed123", "count": 450},
                {"channel": "lobelia4cosmetics", "count": 380},
                {"channel": "tikvahpharma", "count": 241}
            ]
        }
    }

@app.get("/api/v1/messages")
async def get_messages(limit: int = 50, channel: str = None):
    """Get Telegram messages"""
    # Mock data
    messages = []
    
    sample_channels = ["chemed123", "lobelia4cosmetics", "tikvahpharma"]
    
    for i in range(min(limit, 20)):
        channel_name = channel if channel else sample_channels[i % len(sample_channels)]
        messages.append({
            "message_id": f"msg_{i:04d}",
            "channel_name": channel_name,
            "message_text": f"Sample message {i} from {channel_name} about medical products.",
            "message_date": "2024-01-15",
            "views": 100 + (i * 10),
            "forwards": 5 + (i % 10),
            "has_image": i % 3 == 0,
            "hashtags": ["#medical", "#health", "#pharmacy"] if i % 2 == 0 else ["#cosmetic", "#beauty"]
        })
    
    if channel:
        messages = [m for m in messages if m["channel_name"] == channel]
    
    return {
        "success": True,
        "count": len(messages),
        "limit": limit,
        "channel_filter": channel,
        "messages": messages[:limit]
    }

@app.get("/api/v1/search")
async def search(
    q: str,
    search_in: str = "all",  # all, messages, detections
    limit: int = 20
):
    """Search across messages and detections"""
    return {
        "success": True,
        "query": q,
        "search_in": search_in,
        "limit": limit,
        "results": {
            "messages": [
                {
                    "id": "msg_001",
                    "channel": "chemed123",
                    "text": f"Found message containing '{q}'",
                    "date": "2024-01-15",
                    "relevance": 0.85
                }
            ],
            "detections": [
                {
                    "id": "det_001",
                    "channel": "lobelia4cosmetics",
                    "class": f"Object related to '{q}'",
                    "confidence": 0.92,
                    "date": "2024-01-15",
                    "relevance": 0.78
                }
            ]
        }
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
