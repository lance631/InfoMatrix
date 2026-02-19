from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import blogs, posts, health
from app.config import settings

app = FastAPI(
    title="InfoMatrix API",
    description="技术博客RSS聚合器API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(blogs.router, prefix="/api/blogs", tags=["blogs"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])

@app.on_event("startup")
async def startup_event():
    """启动时初始化RSS源"""
    from app.services.rss_service import rss_service
    await rss_service.initialize_feeds()

@app.get("/")
async def root():
    return {
        "message": "InfoMatrix API",
        "version": "1.0.0",
        "docs": "/docs"
    }
