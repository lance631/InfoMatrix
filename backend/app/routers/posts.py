"""
Posts API router.

Endpoints for retrieving and refreshing RSS posts.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import db_service, rss_service
from app.models.schemas import BlogPost

router = APIRouter(tags=["posts"])


# ============================================================================
# Pydantic Models
# ============================================================================

class PostResponse(BaseModel):
    """Response model for a post."""
    id: str
    blog_id: str
    blog_name: str
    title: str
    link: str
    summary: str | None
    content: str | None
    published: datetime | None
    author: str | None
    category: str | None

    class Config:
        from_attributes = True


class RefreshResponse(BaseModel):
    """Response model for refresh endpoint."""
    message: str
    results: dict
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class StatsResponse(BaseModel):
    """Response model for stats endpoint."""
    total_blogs: int
    total_posts: int
    total_featured: int
    posts_by_category: dict
    redis_connected: bool
    cache_ttl: int


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=List[PostResponse])
async def get_posts(
    blog_id: Optional[str] = Query(None, description="Blog UUID"),
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(100, ge=1, le=500, description="Max number of posts"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get posts with optional filters.

    Args:
        blog_id: Optional blog UUID to filter by
        category: Optional category to filter by
        limit: Max number of posts to return
        offset: Number of posts to skip
        db: Database session

    Returns:
        List of posts
    """
    # Convert blog_id string to UUID if provided
    blog_uuid = None
    if blog_id:
        try:
            blog_uuid = uuid.UUID(blog_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid blog_id format")

    # Get posts from database
    posts = await db_service.get_posts(
        db,
        blog_id=blog_uuid,
        category=category,
        limit=limit,
        offset=offset
    )

    # Convert to response format
    result = []
    for post in posts:
        result.append(PostResponse(
            id=str(post.id),
            blog_id=str(post.blog_id),
            blog_name=post.blog.name,
            title=post.title,
            link=post.link,
            summary=post.summary,
            content=post.content,
            published=post.published_at,
            author=post.author,
            category=post.blog.category
        ))

    return result


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_feeds(db: AsyncSession = Depends(get_db)):
    """
    Refresh all RSS feeds and store in database.

    Args:
        db: Database session

    Returns:
        Refresh results with post counts per feed
    """
    results = await rss_service.refresh_all_feeds(session=db)

    return RefreshResponse(
        message="RSS feeds refreshed successfully",
        results=results
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Get application statistics.

    Args:
        db: Database session

    Returns:
        Application statistics
    """
    db_stats = await db_service.get_stats(db)
    rss_stats = await rss_service.get_stats()

    return StatsResponse(
        total_blogs=db_stats["total_blogs"],
        total_posts=db_stats["total_posts"],
        total_featured=db_stats["total_featured"],
        posts_by_category=db_stats["posts_by_category"],
        redis_connected=rss_stats["redis_connected"],
        cache_ttl=rss_stats["cache_ttl"]
    )


@router.get("/search", response_model=List[PostResponse])
async def search_posts(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Full-text search across posts.

    Args:
        q: Search query (supports PostgreSQL tsquery syntax)
        limit: Max number of results
        db: Database session

    Returns:
        List of matching posts
    """
    posts = await db_service.search_posts(db, query=q, limit=limit)

    result = []
    for post in posts:
        result.append(PostResponse(
            id=str(post.id),
            blog_id=str(post.blog_id),
            blog_name=post.blog.name,
            title=post.title,
            link=post.link,
            summary=post.summary,
            content=post.content,
            published=post.published_at,
            author=post.author,
            category=post.blog.category
        ))

    return result
