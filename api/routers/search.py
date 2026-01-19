"""
Search endpoints for detections
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import time
from datetime import datetime, date
from typing import List, Optional

from api.database import get_db
from api.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from src.common.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Mock search data (replace with database queries)
mock_detections = [
    {
        "image_path": "images/chemed_pharmacy/med1.jpg",
        "image_name": "med1.jpg",
        "channel_name": "chemed_pharmacy",
        "detected_class": "medicine",
        "confidence": 0.85,
        "detection_date": "2024-01-15T10:30:00",
        "bounding_box": {"x": 0.5, "y": 0.5, "width": 0.2, "height": 0.3},
    },
    {
        "image_path": "images/chemed_pharmacy/bottle1.jpg",
        "image_name": "bottle1.jpg",
        "channel_name": "chemed_pharmacy",
        "detected_class": "bottle",
        "confidence": 0.92,
        "detection_date": "2024-01-14T14:20:00",
        "bounding_box": {"x": 0.3, "y": 0.7, "width": 0.25, "height": 0.4},
    },
    {
        "image_path": "images/lobelia_cosmetics/cream1.jpg",
        "image_name": "cream1.jpg",
        "channel_name": "lobelia_cosmetics",
        "detected_class": "cream",
        "confidence": 0.78,
        "detection_date": "2024-01-13T09:45:00",
        "bounding_box": {"x": 0.4, "y": 0.5, "width": 0.15, "height": 0.25},
    },
    {
        "image_path": "images/lobelia_cosmetics/bottle2.jpg",
        "image_name": "bottle2.jpg",
        "channel_name": "lobelia_cosmetics",
        "detected_class": "bottle",
        "confidence": 0.88,
        "detection_date": "2024-01-12T11:15:00",
        "bounding_box": {"x": 0.6, "y": 0.4, "width": 0.3, "height": 0.2},
    },
    {
        "image_path": "images/tikvah_pharma/syringe1.jpg",
        "image_name": "syringe1.jpg",
        "channel_name": "tikvah_pharma",
        "detected_class": "syringe",
        "confidence": 0.91,
        "detection_date": "2024-01-11T16:30:00",
        "bounding_box": {"x": 0.5, "y": 0.6, "width": 0.1, "height": 0.2},
    },
]

@router.post("/search", response_model=SearchResponse)
async def search_detections(
    search_request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search detections with advanced filtering
    
    - **query**: Search query (searches in detected_class and channel_name)
    - **channel_names**: Filter by specific channels
    - **start_date**: Filter by start date
    - **end_date**: Filter by end date
    - **min_confidence**: Minimum confidence score
    - **max_confidence**: Maximum confidence score
    - **limit**: Maximum number of results
    - **offset**: Pagination offset
    """
    start_time = time.time()
    
    try:
        logger.info(
            "Searching detections",
            query=search_request.query,
            filters={
                "channel_names": search_request.channel_names,
                "start_date": search_request.start_date,
                "end_date": search_request.end_date,
                "min_confidence": search_request.min_confidence,
                "max_confidence": search_request.max_confidence,
            },
        )
        
        # Apply filters to mock data
        filtered_results = []
        
        for detection in mock_detections:
            # Apply query filter
            query_lower = search_request.query.lower()
            if query_lower and query_lower not in detection["detected_class"].lower() and query_lower not in detection["channel_name"].lower():
                continue
            
            # Apply channel filter
            if search_request.channel_names and detection["channel_name"] not in search_request.channel_names:
                continue
            
            # Apply date filter
            if search_request.start_date:
                detection_date = datetime.fromisoformat(detection["detection_date"]).date()
                if detection_date < search_request.start_date:
                    continue
            
            if search_request.end_date:
                detection_date = datetime.fromisoformat(detection["detection_date"]).date()
                if detection_date > search_request.end_date:
                    continue
            
            # Apply confidence filter
            if search_request.min_confidence and detection["confidence"] < search_request.min_confidence:
                continue
            
            if search_request.max_confidence and detection["confidence"] > search_request.max_confidence:
                continue
            
            filtered_results.append(detection)
        
        # Apply pagination
        total = len(filtered_results)
        paginated_results = filtered_results[
            search_request.offset:search_request.offset + search_request.limit
        ]
        
        search_time = (time.time() - start_time) * 1000
        
        logger.info(
            "Search completed",
            results_found=total,
            results_returned=len(paginated_results),
            search_time_ms=search_time,
        )
        
        return SearchResponse(
            results=[SearchResult(**result) for result in paginated_results],
            total=total,
            query=search_request.query,
            search_time_ms=search_time,
        )
        
    except Exception as e:
        logger.error("Search failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search/quick")
async def quick_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick search with autocomplete suggestions
    
    - **q**: Search query
    - **limit**: Maximum number of suggestions
    """
    try:
        # Mock implementation - in real app, search database
        suggestions = []
        
        # Search in channel names
        channels = ["chemed_pharmacy", "lobelia_cosmetics", "tikvah_pharma"]
        for channel in channels:
            if q.lower() in channel.lower():
                suggestions.append({
                    "type": "channel",
                    "value": channel,
                    "label": f"Channel: {channel}",
                })
        
        # Search in object names
        objects = ["medicine", "bottle", "cream", "syringe", "box", "ointment", "pill"]
        for obj in objects:
            if q.lower() in obj.lower():
                suggestions.append({
                    "type": "object",
                    "value": obj,
                    "label": f"Object: {obj}",
                })
        
        # Limit results
        suggestions = suggestions[:limit]
        
        return {
            "query": q,
            "suggestions": suggestions,
            "count": len(suggestions),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error("Quick search failed", error=str(e))
        raise HTTPException(status_code=500, detail="Quick search failed")

@router.get("/search/filters")
async def get_search_filters(db: AsyncSession = Depends(get_db)):
    """
    Get available filters for search
    """
    try:
        # Mock implementation - in real app, get from database
        return {
            "channels": [
                {"name": "chemed_pharmacy", "display_name": "Chemed Pharmacy", "count": 650},
                {"name": "lobelia_cosmetics", "display_name": "Lobelia Cosmetics", "count": 350},
                {"name": "tikvah_pharma", "display_name": "Tikvah Pharma", "count": 250},
            ],
            "objects": [
                {"name": "bottle", "category": "packaging", "count": 420},
                {"name": "medicine", "category": "medical", "count": 380},
                {"name": "cream", "category": "cosmetic", "count": 210},
                {"name": "box", "category": "packaging", "count": 180},
                {"name": "syringe", "category": "medical", "count": 120},
            ],
            "confidence_ranges": [
                {"min": 0.9, "max": 1.0, "label": "Very High (90-100%)"},
                {"min": 0.8, "max": 0.9, "label": "High (80-90%)"},
                {"min": 0.6, "max": 0.8, "label": "Medium (60-80%)"},
                {"min": 0.0, "max": 0.6, "label": "Low (0-60%)"},
            ],
            "date_range": {
                "min": "2024-01-01",
                "max": "2024-01-18",
            },
        }
        
    except Exception as e:
        logger.error("Failed to get search filters", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get search filters")
