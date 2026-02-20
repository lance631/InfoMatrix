from pydantic_settings import BaseSettings
from typing import List
import os


def _convert_postgres_url(url: str) -> str:
    """
    Convert postgres:// URL to postgresql+asyncpg:// URL for async SQLAlchemy.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    # Database配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost:5432/infomatrix"
    )

    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Debug模式
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # RSS缓存时间（秒）
    CACHE_TTL: int = 3600  # 1小时

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

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

    @property
    def async_database_url(self) -> str:
        """Get async-compatible database URL."""
        return _convert_postgres_url(self.DATABASE_URL)


# Initialize settings with CORS origins from environment
_settings = Settings()
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    _settings.CORS_ORIGINS.extend([origin.strip() for origin in cors_origins_env.split(",")])

settings = _settings
