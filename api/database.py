from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging

from api.config import settings
from api.models.base import Base
from api.models.channel import Channel
from api.models.detection import RawImageDetection, DetectionAggregate
from api.models.message import Message

logger = logging.getLogger(__name__)

# Convert sync PostgreSQL URL to async
def get_async_database_url() -> str:
    """Convert sync database URL to async format"""
    if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql://"):
        return settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    return settings.DATABASE_URL

# Create async engine
DATABASE_URL = get_async_database_url()
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def execute_read_query(query: str, params: dict = None) -> list:
    """Execute raw SQL query"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(query), params or {})
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

async def check_database_health() -> bool:
    """Check database connection"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

async def get_database_stats() -> dict:
    """Get database statistics"""
    try:
        stats = {}
        async with AsyncSessionLocal() as session:
            # Check if tables exist and get counts
            tables = ["dim_channels", "fct_messages", "raw_image_detections", "detection_aggregates"]
            
            for table in tables:
                try:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    stats[table] = count
                except Exception:
                    stats[table] = "Table not found"
            
            return stats
            
    except Exception as e:
        logger.error(f"Failed to get database stats: {str(e)}")
        return {"error": str(e)}
