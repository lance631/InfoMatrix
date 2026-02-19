from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BlogSource(BaseModel):
    id: str
    name: str
    url: str
    category: str
    description: Optional[str] = None

class BlogPost(BaseModel):
    id: str
    blog_id: str
    blog_name: str
    title: str
    link: str
    summary: str
    published: Optional[datetime] = None
    author: Optional[str] = None
    category: str

class PaginatedResponse(BaseModel):
    items: List[BlogPost]
    total: int
    page: int
    page_size: int

class HealthResponse(BaseModel):
    status: str
    redis_connected: bool
    total_blogs: int
    total_posts: int
