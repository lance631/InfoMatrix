from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import blogs, posts, health, featured
from app.config import settings
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    from app.services.rss_service import rss_service
    await rss_service.initialize_feeds()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="InfoMatrix API",
    description="技术博客RSS聚合器API",
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(blogs.router, prefix="/api/blogs")
app.include_router(posts.router, prefix="/api/posts")
app.include_router(featured.router, prefix="/api/featured")

@app.get("/")
async def root():
    return {
        "message": "InfoMatrix API",
        "version": "1.0.0",
        "docs": "/docs"
    }
