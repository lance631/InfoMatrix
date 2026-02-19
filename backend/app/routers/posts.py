from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.schemas import BlogPost, PaginatedResponse
from app.services.rss_service import rss_service

router = APIRouter()

@router.get("", response_model=List[BlogPost])
async def get_posts(
    blog_id: Optional[str] = Query(None, description="博客ID"),
    category: Optional[str] = Query(None, description="分类"),
    limit: int = Query(100, ge=1, le=500, description="返回数量限制")
):
    """获取文章列表"""
    posts = await rss_service.get_cached_posts(blog_id)

    # 按分类过滤
    if category:
        posts = [p for p in posts if p.get("category") == category]

    # 按发布时间排序
    posts.sort(key=lambda x: x.get("published") or "", reverse=True)

    # 限制返回数量
    posts = posts[:limit]

    return [
        BlogPost(**post) for post in posts
    ]

@router.post("/refresh")
async def refresh_feeds():
    """刷新所有RSS源"""
    results = await rss_service.refresh_all_feeds()
    return {
        "message": "RSS源已刷新",
        "results": results
    }

@router.get("/stats")
async def get_stats():
    """获取统计信息"""
    return await rss_service.get_stats()
