from fastapi import APIRouter
from typing import List
from app.models.schemas import BlogSource
from app.services.rss_service import rss_service

router = APIRouter()

@router.get("", response_model=List[BlogSource])
async def get_blogs():
    """获取所有博客源列表"""
    blogs = rss_service.get_all_blogs()
    return [
        BlogSource(
            id=blog["id"],
            name=blog["name"],
            url=blog["url"],
            category=blog["category"],
            description=blog.get("description")
        )
        for blog in blogs
    ]

@router.get("/categories")
async def get_categories():
    """获取所有分类"""
    blogs = rss_service.get_all_blogs()
    categories = list(set(blog["category"] for blog in blogs))
    return {"categories": categories}
