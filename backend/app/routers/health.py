"""
Health check API router.

Provides health status and connectivity information.
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.services.rss_service import rss_service

router = APIRouter(tags=["health"])


# ============================================================================
# Pydantic Models
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status: healthy, degraded, or unhealthy")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    database: dict = Field(default_factory=dict)
    redis: dict = Field(default_factory=dict)
    rss: dict = Field(default_factory=dict)


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.

    Checks database, Redis, and RSS service status.

    Args:
        db: Database session

    Returns:
        Health status with component details
    """
    health_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {},
        "redis": {},
        "rss": {}
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health_info["database"] = {
            "status": "connected",
            "message": "Database connection OK"
        }
    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["database"] = {
            "status": "disconnected",
            "message": str(e)
        }

    # Check Redis
    try:
        rss_stats = await rss_service.get_stats()
        if rss_stats["redis_connected"]:
            health_info["redis"] = {
                "status": "connected",
                "message": "Redis connection OK"
            }
        else:
            health_info["status"] = "degraded" if health_info["status"] == "healthy" else health_info["status"]
            health_info["redis"] = {
                "status": "disconnected",
                "message": "Redis not available (using database fallback)"
            }
    except Exception as e:
        health_info["status"] = "degraded" if health_info["status"] == "healthy" else health_info["status"]
        health_info["redis"] = {
            "status": "error",
            "message": str(e)
        }

    # Check RSS service
    try:
        rss_stats = await rss_service.get_stats()
        health_info["rss"] = {
            "status": "ok",
            "total_feeds": rss_stats["total_feeds"],
            "cache_ttl": rss_stats["cache_ttl"]
        }
    except Exception as e:
        health_info["status"] = "degraded" if health_info["status"] == "healthy" else health_info["status"]
        health_info["rss"] = {
            "status": "error",
            "message": str(e)
        }

    return HealthResponse(**health_info)
