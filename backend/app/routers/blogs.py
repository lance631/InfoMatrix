"""
Blogs API router.

Endpoints for retrieving blog source information.
"""
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import db_service, rss_service

router = APIRouter(tags=["blogs"])


# ============================================================================
# Pydantic Models
# ============================================================================

class BlogSource(BaseModel):
    """Blog source information."""
    id: str
    name: str
    url: str
    category: str | None
    description: str | None


class CategoriesResponse(BaseModel):
    """Categories response."""
    categories: List[str]


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=List[BlogSource])
async def get_blogs():
    """
    Get all blog source configurations.

    Returns:
        List of blog sources from config
    """
    blogs = rss_service.get_all_blogs()
    return [
        BlogSource(
            id=blog["id"],
            name=blog["name"],
            url=blog["url"],
            category=blog.get("category"),
            description=blog.get("description")
        )
        for blog in blogs
    ]


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Get all unique blog categories from database.

    Args:
        db: Database session

    Returns:
        List of unique categories
    """
    categories = await db_service.get_categories(db)
    return CategoriesResponse(categories=categories)
