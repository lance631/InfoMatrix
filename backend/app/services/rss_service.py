import feedparser
import httpx
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional
from app.config import settings
from app.services import db_service  # 通过 service 操作数据库
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

class RSSService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.feeds: Dict[str, dict] = {}

    async def init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            print("✓ Redis连接成功")
        except Exception as e:
            print(f"✗ Redis连接失败: {e}")
            self.redis_client = None

    async def initialize_feeds(self):
        """初始化RSS源"""
        await self.init_redis()
        for feed in settings.RSS_FEEDS:
            self.feeds[feed["id"]] = feed
            # 仅缓存，不写数据库
            await self.fetch_and_cache_feed(feed["id"])
        print(f"✓ 已加载 {len(self.feeds)} 个RSS源")

    async def fetch_feed(self, url: str) -> Optional[dict]:
        """获取RSS源"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                return feedparser.parse(response.content)
            except Exception as e:
                print(f"获取RSS源失败 {url}: {e}")
                return None

    def generate_post_id(self, blog_id: str, link: str) -> str:
        """生成文章唯一ID"""
        content = f"{blog_id}:{link}"
        return hashlib.md5(content.encode()).hexdigest()

    async def fetch_and_cache_feed(
        self,
        blog_id: str,
        session: Optional[AsyncSession] = None
    ) -> List[dict]:
        """获取RSS源并缓存/写入数据库"""
        if blog_id not in self.feeds:
            return []

        feed_info = self.feeds[blog_id]
        feed_data = await self.fetch_feed(feed_info["url"])
        if not feed_data:
            return []

        posts = []

        # 先确保博客存在数据库
        if session:
            await db_service.create_blog_if_not_exists(
                session=session,
                blog_id=blog_id,
                name=feed_info["name"],
                rss_url=feed_info["url"],
                category=feed_info.get("category"),
                site_url=feed_info.get("site_url"),
                description=feed_info.get("description")
            )

        for entry in feed_data.entries[:50]:
            post_id = self.generate_post_id(blog_id, entry.link)
            published = self._parse_date(entry.get("published"))

            post = {
                "id": post_id,
                "blog_id": blog_id,
                "blog_name": feed_info["name"],
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", ""),
                "content": entry.get("content", [{}])[0].get("value", "") if "content" in entry else "",
                "published": published,
                "author": entry.get("author"),
                "category": feed_info.get("category")
            }
            posts.append(post)

            # 写入数据库
            if session:
                await db_service.upsert_post(
                    session=session,
                    post_id=post_id,
                    blog_id=blog_id,
                    title=entry.title,
                    link=entry.link,
                    summary=entry.get("summary", ""),
                    content=post["content"],
                    published=published,
                    author=entry.get("author")
                )

        # 缓存到 Redis
        if self.redis_client:
            cache_key = f"posts:{blog_id}"
            await self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL,
                json.dumps(posts, default=str)
            )

            # 缓存所有文章ID的集合
            for post in posts:
                await self.redis_client.sadd("posts:all", post["id"])

        return posts

    async def get_cached_posts(self, blog_id: Optional[str] = None) -> List[dict]:
        """获取缓存的文章"""
        if not self.redis_client:
            return await self.fetch_and_cache_feed(blog_id) if blog_id else []

        if blog_id:
            cache_key = f"posts:{blog_id}"
            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            return await self.fetch_and_cache_feed(blog_id)
        else:
            all_posts = []
            for bid in self.feeds.keys():
                cache_key = f"posts:{bid}"
                cached = await self.redis_client.get(cache_key)
                if cached:
                    all_posts.extend(json.loads(cached))
            return all_posts

    async def refresh_all_feeds(self, session: Optional[AsyncSession] = None) -> Dict[str, int]:
        """刷新所有RSS源，可写入数据库"""
        results = {}
        for blog_id in self.feeds.keys():
            posts = await self.fetch_and_cache_feed(blog_id, session=session)
            results[blog_id] = len(posts)
        return results

    def get_all_blogs(self) -> List[dict]:
        """获取所有博客源"""
        return list(self.feeds.values())

    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """解析日期"""
        if not date_str:
            return None
        try:
            dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
            return dt.isoformat()
        except:
            return date_str

    async def get_stats(self) -> dict:
        """获取统计信息"""
        all_posts = await self.get_cached_posts()
        return {
            "total_blogs": len(self.feeds),
            "total_posts": len(all_posts),
            "redis_connected": self.redis_client is not None
        }

# 全局实例
rss_service = RSSService()