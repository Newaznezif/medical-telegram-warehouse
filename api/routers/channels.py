"""
Channel management endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from api.database import get_db
from api.schemas import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelListResponse,
    SuccessResponse,
)
from src.common.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Mock channel data (replace with database model)
channels_db = {
    1: {
        "id": 1,
        "name": "chemed_pharmacy",
        "display_name": "Chemed Pharmacy",
        "category": "medical",
        "description": "Medical supplies and pharmacy products",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-15T00:00:00",
        "detection_count": 650,
    },
    2: {
        "id": 2,
        "name": "lobelia_cosmetics",
        "display_name": "Lobelia Cosmetics",
        "category": "cosmetic",
        "description": "Cosmetic and beauty products",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-15T00:00:00",
        "detection_count": 350,
    },
    3: {
        "id": 3,
        "name": "tikvah_pharma",
        "display_name": "Tikvah Pharma",
        "category": "medical",
        "description": "Pharmaceutical products",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-15T00:00:00",
        "detection_count": 250,
    },
}

@router.get("/channels", response_model=ChannelListResponse)
async def list_channels(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Show only active channels"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all channels with pagination and filtering
    
    - **skip**: Number of items to skip (pagination)
    - **limit**: Number of items to return (pagination)
    - **category**: Filter by channel category
    - **active_only**: Show only active channels
    """
    try:
        # Filter channels
        filtered_channels = []
        for channel in channels_db.values():
            if active_only and not channel["is_active"]:
                continue
            if category and channel["category"] != category:
                continue
            filtered_channels.append(channel)
        
        # Apply pagination
        total = len(filtered_channels)
        items = filtered_channels[skip:skip + limit]
        
        logger.info(
            "Listed channels",
            total=total,
            returned=len(items),
            skip=skip,
            limit=limit,
        )
        
        return ChannelListResponse(
            items=[ChannelResponse(**item) for item in items],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 1,
        )
        
    except Exception as e:
        logger.error("Failed to list channels", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list channels")

@router.get("/channels/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific channel by ID
    """
    try:
        if channel_id not in channels_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Channel with ID {channel_id} not found"
            )
        
        logger.info("Retrieved channel", channel_id=channel_id)
        return ChannelResponse(**channels_db[channel_id])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get channel {channel_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get channel")

@router.post("/channels", response_model=ChannelResponse)
async def create_channel(
    channel: ChannelCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new channel
    
    - **name**: Unique channel identifier (required)
    - **display_name**: Human-readable channel name
    - **category**: Channel category (medical, cosmetic, mixed, other)
    - **description**: Channel description
    - **is_active**: Whether the channel is active
    """
    try:
        # Check if channel name already exists
        for existing_channel in channels_db.values():
            if existing_channel["name"] == channel.name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Channel with name '{channel.name}' already exists"
                )
        
        # Create new channel
        new_id = max(channels_db.keys()) + 1
        now = "2024-01-18T00:00:00"  # In real implementation, use datetime.utcnow()
        
        new_channel = {
            "id": new_id,
            "name": channel.name,
            "display_name": channel.display_name,
            "category": channel.category,
            "description": channel.description,
            "is_active": channel.is_active,
            "created_at": now,
            "updated_at": now,
            "detection_count": 0,
        }
        
        channels_db[new_id] = new_channel
        
        logger.info("Created new channel", channel_id=new_id, channel_name=channel.name)
        return ChannelResponse(**new_channel)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create channel", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create channel")

@router.put("/channels/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_update: ChannelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing channel
    """
    try:
        if channel_id not in channels_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Channel with ID {channel_id} not found"
            )
        
        # Update channel fields
        channel = channels_db[channel_id]
        update_data = channel_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                channel[field] = value
        
        channel["updated_at"] = "2024-01-18T00:00:00"  # In real implementation, use datetime.utcnow()
        
        logger.info("Updated channel", channel_id=channel_id, updates=update_data)
        return ChannelResponse(**channel)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update channel {channel_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update channel")

@router.delete("/channels/{channel_id}", response_model=SuccessResponse)
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a channel (soft delete by marking as inactive)
    """
    try:
        if channel_id not in channels_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Channel with ID {channel_id} not found"
            )
        
        # Mark as inactive instead of deleting
        channel = channels_db[channel_id]
        channel["is_active"] = False
        channel["updated_at"] = "2024-01-18T00:00:00"
        
        logger.info("Deleted channel", channel_id=channel_id)
        return SuccessResponse(
            success=True,
            message=f"Channel {channel_id} deleted successfully",
            timestamp="2024-01-18T00:00:00",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete channel {channel_id}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete channel")

@router.get("/channels/{channel_name}/stats")
async def get_channel_stats(
    channel_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics for a specific channel
    """
    try:
        # Find channel by name
        channel = None
        for ch in channels_db.values():
            if ch["name"] == channel_name:
                channel = ch
                break
        
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Channel '{channel_name}' not found"
            )
        
        # Mock statistics (replace with actual database queries)
        stats = {
            "channel": channel["name"],
            "display_name": channel["display_name"],
            "category": channel["category"],
            "total_detections": channel["detection_count"],
            "last_30_days": 120 if channel_name == "chemed_pharmacy" else 80,
            "avg_confidence": 0.82 if channel_name == "chemed_pharmacy" else 0.75,
            "top_objects": ["bottle", "medicine", "box"] if channel_name == "chemed_pharmacy" else ["cream", "bottle", "ointment"],
            "object_count": 5 if channel_name == "chemed_pharmacy" else 4,
            "detection_trend": "increasing",
            "last_updated": channel["updated_at"],
        }
        
        logger.info("Retrieved channel stats", channel_name=channel_name)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stats for channel {channel_name}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get channel statistics")
