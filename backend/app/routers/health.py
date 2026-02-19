from fastapi import APIRouter, HTTPException
from app.models.schemas import HealthResponse
from app.services.rss_service import rss_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    try:
        stats = await rss_service.get_stats()
        return HealthResponse(
            status="healthy" if stats["redis_connected"] else "degraded",
            redis_connected=stats["redis_connected"],
            total_blogs=stats["total_blogs"],
            total_posts=stats["total_posts"]
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
