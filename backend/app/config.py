from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # RSS缓存时间（秒）
    CACHE_TTL: int = 3600  # 1小时

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # 添加环境变量中的CORS origins
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    if cors_origins_env:
        CORS_ORIGINS.extend([origin.strip() for origin in cors_origins_env.split(",")])

    # RSS源列表（可以从环境变量或数据库读取）
    RSS_FEEDS: List[dict] = [
        {
            "id": "阮一峰",
            "name": "阮一峰的网络日志",
            "url": "https://www.ruanyifeng.com/blog/atom.xml",
            "category": "技术"
        },
        {
            "id": "v2ex",
            "name": "V2EX",
            "url": "https://www.v2ex.com/index.xml",
            "category": "综合"
        },
        {
            "id": "juejin",
            "name": "掘金前端",
            "url": "https://frontendjs.org/feed.xml",
            "category": "前端"
        }
    ]

    class Config:
        env_file = ".env"

settings = Settings()
