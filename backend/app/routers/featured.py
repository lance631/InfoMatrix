"""
Featured posts API router.

Endpoints for managing weekly featured posts.
"""
import uuid
from datetime import date, datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import db_service

router = APIRouter(tags=["featured"])


# ============================================================================
# Pydantic Models
# ============================================================================

class FeaturedPostCreate(BaseModel):
    """Request model for adding a featured post."""
    post_id: str = Field(..., description="UUID of the post to feature")
    week_start: date = Field(..., description="Week start date (YYYY-MM-DD)")
    editor_notes: str | None = Field(None, description="Optional editor notes")
    order_index: int | None = Field(None, description="Display order within the week")


class FeaturedPostResponse(BaseModel):
    """Response model for a featured post."""
    id: int
    post_id: str
    week_start: date
    editor_notes: str | None
    order_index: int
    created_at: datetime

    # Nested post information
    title: str
    link: str
    blog_name: str

    class Config:
        from_attributes = True


class FeaturedPostListResponse(BaseModel):
    """Response model for a list of featured posts."""
    week_start: date
    posts: List[FeaturedPostResponse]


class WeekInfo(BaseModel):
    """Information about a week with featured posts."""
    week_start: date
    post_count: int


# ============================================================================
# Endpoints
# ============================================================================

@router.post("", response_model=FeaturedPostResponse, status_code=201)
async def add_featured_post(
    data: FeaturedPostCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Add a post to featured.

    Args:
        data: Featured post creation data
        db: Database session

    Returns:
        Created featured post

    Raises:
        400: If post is already featured for this week
        404: If post doesn't exist
    """
    try:
        post_id = uuid.UUID(data.post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post_id format")

    # Verify post exists
    post = await db_service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        featured = await db_service.add_featured_post(
            db,
            post_id=post_id,
            week_start=data.week_start,
            editor_notes=data.editor_notes,
            order_index=data.order_index
        )
        # Refresh to get relationships
        await db.refresh(featured)
        await db.refresh(featured.post)
        await db.refresh(featured.post.blog)

        return FeaturedPostResponse(
            id=featured.id,
            post_id=str(featured.post_id),
            week_start=featured.week_start,
            editor_notes=featured.editor_notes,
            order_index=featured.order_index,
            created_at=featured.created_at,
            title=featured.post.title,
            link=featured.post.link,
            blog_name=featured.post.blog.name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{week_start}", response_model=FeaturedPostListResponse)
async def get_featured_posts(
    week_start: date,
    db: AsyncSession = Depends(get_db)
):
    """
    Get featured posts for a specific week.

    Args:
        week_start: Week start date (YYYY-MM-DD)
        db: Database session

    Returns:
        List of featured posts for the week
    """
    featured_posts = await db_service.get_featured_posts(db, week_start)

    posts = []
    for fp in featured_posts:
        posts.append(FeaturedPostResponse(
            id=fp.id,
            post_id=str(fp.post_id),
            week_start=fp.week_start,
            editor_notes=fp.editor_notes,
            order_index=fp.order_index,
            created_at=fp.created_at,
            title=fp.post.title,
            link=fp.post.link,
            blog_name=fp.post.blog.name
        ))

    return FeaturedPostListResponse(week_start=week_start, posts=posts)


@router.get("", response_model=List[WeekInfo])
async def list_featured_weeks(
    db: AsyncSession = Depends(get_db)
):
    """
    List all weeks that have featured posts.

    Args:
        db: Database session

    Returns:
        List of week information
    """
    weeks = await db_service.get_featured_weeks(db)

    # Get post count for each week
    result = []
    for week in weeks:
        posts = await db_service.get_featured_posts(db, week)
        result.append(WeekInfo(week_start=week, post_count=len(posts)))

    return result


@router.delete("/{featured_id}", status_code=204)
async def remove_featured_post(
    featured_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a post from featured.

    Args:
        featured_id: ID of the featured post entry
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        404: If featured post not found
    """
    removed = await db_service.remove_featured_post(db, featured_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Featured post not found")
    return None
