"""
RSS feed fetching and parsing service.

This service handles:
- Fetching RSS/Atom feeds from configured sources
- Parsing feed entries
- Extracting thumbnail images from content
- Storing posts in PostgreSQL (idempotent)
- Caching in Redis for fast reads
"""
import feedparser
import httpx
import hashlib
import json
import re
import uuid as uuid_lib
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services import db_service
import redis.asyncio as redis


class RSSService:
    """Service for fetching and caching RSS feeds."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.feeds: Dict[str, dict] = {}  # blog_id -> feed config

    async def init_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            print("✓ Redis connected")
        except Exception as e:
            print(f"✗ Redis connection failed: {e}")
            self.redis_client = None

    async def initialize_feeds(self) -> None:
        """Initialize RSS feeds from config and cache them."""
        await self.init_redis()

        # Load feeds from config
        for feed in settings.RSS_FEEDS:
            self.feeds[feed["id"]] = feed

        print(f"✓ Loaded {len(self.feeds)} RSS sources")

    async def fetch_feed(self, url: str) -> Optional[dict]:
        """
        Fetch an RSS feed from URL.

        Args:
            url: RSS feed URL

        Returns:
            Parsed feed data or None if failed
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return feedparser.parse(response.content)
            except Exception as e:
                print(f"✗ Failed to fetch RSS feed {url}: {e}")
                return None

    def generate_post_id(self, blog_id: str, link: str) -> uuid_lib.UUID:
        """
        Generate deterministic UUID for a post.

        Uses MD5 hash of blog_id:link to ensure idempotency.
        The same blog + link will always generate the same UUID.

        Args:
            blog_id: Blog identifier
            link: Article URL

        Returns:
            UUID for the post
        """
        content = f"{blog_id}:{link}"
        hash_hex = hashlib.md5(content.encode()).hexdigest()
        return uuid_lib.UUID(hex=hash_hex)

    def generate_blog_id(self, feed_id: str) -> uuid_lib.UUID:
        """
        Generate deterministic UUID for a blog.

        Uses MD5 hash of the feed_id from config.

        Args:
            feed_id: Feed identifier from config

        Returns:
            UUID for the blog
        """
        hash_hex = hashlib.md5(feed_id.encode()).hexdigest()
        return uuid_lib.UUID(hex=hash_hex)

    async def fetch_and_cache_feed(
        self,
        feed_id: str,
        session: Optional[AsyncSession] = None
    ) -> List[dict]:
        """
        Fetch RSS feed, store in database, and cache in Redis.

        Args:
            feed_id: Feed identifier from config
            session: Optional database session for persistence

        Returns:
            List of post dictionaries
        """
        if feed_id not in self.feeds:
            return []

        feed_info = self.feeds[feed_id]
        feed_data = await self.fetch_feed(feed_info["url"])
        if not feed_data:
            return []

        # Generate blog UUID
        blog_id = self.generate_blog_id(feed_id)

        # Ensure blog exists in database
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

        posts = []

        for entry in feed_data.entries[:50]:
            if not hasattr(entry, 'link'):
                continue

            post_id = self.generate_post_id(feed_id, entry.link)
            published = self._parse_date(entry.get("published"))
            thumbnail = self._extract_thumbnail(entry)

            post = {
                "id": str(post_id),
                "blog_id": str(blog_id),
                "blog_name": feed_info["name"],
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", ""),
                "content": self._extract_content(entry),
                "thumbnail": thumbnail,
                "published": published,
                "author": entry.get("author"),
                "category": feed_info.get("category")
            }
            posts.append(post)

            # Store in database
            if session:
                await db_service.upsert_post(
                    session=session,
                    post_id=post_id,
                    blog_id=blog_id,
                    title=entry.title,
                    link=entry.link,
                    summary=entry.get("summary", ""),
                    content=post["content"],
                    thumbnail=thumbnail,
                    published_at=published,
                    author=entry.get("author")
                )

        # Cache in Redis
        if self.redis_client:
            cache_key = f"posts:{feed_id}"
            await self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL,
                json.dumps(posts, default=str)
            )

        return posts

    def _extract_content(self, entry) -> str:
        """Extract content from RSS entry."""
        if hasattr(entry, 'content') and entry.content:
            return entry.content[0].get('value', '')
        if hasattr(entry, 'summary'):
            return entry.summary
        return ""

    def _extract_thumbnail(self, entry) -> Optional[str]:
        """
        Extract thumbnail URL from RSS entry.

        Tries multiple sources:
        1. media_thumbnail field
        2. media_content field
        3. First <img> tag in content/summary

        Args:
            entry: Feedparser entry object

        Returns:
            Thumbnail URL or None
        """
        # Try media_thumbnail
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            return entry.media_thumbnail[0].get('url')

        # Try media_content
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('type', '').startswith('image/'):
                    return media.get('url')

        # Extract from content
        content = self._extract_content(entry)
        if content:
            # Try multiple img tag patterns
            patterns = [
                r'<img[^>]+src="([^"]+)"',  # Double quotes
                r"<img[^>]+src='([^']+)'",  # Single quotes
            ]

            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    img_url = match.group(1)
                    # Clean URL (remove query params and fragments)
                    img_url = img_url.split('?')[0].split('#')[0]
                    # Verify it's an image
                    if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                        return img_url

        return None

    async def get_cached_posts(self, feed_id: Optional[str] = None) -> List[dict]:
        """
        Get posts from cache or fetch if not cached.

        Args:
            feed_id: Optional feed ID to filter by

        Returns:
            List of post dictionaries
        """
        if not self.redis_client:
            # Fallback: fetch directly (without session = no DB storage)
            if feed_id:
                return await self.fetch_and_cache_feed(feed_id)
            return []

        if feed_id:
            cache_key = f"posts:{feed_id}"
            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            return await self.fetch_and_cache_feed(feed_id)
        else:
            # Get all posts from cache
            all_posts = []
            for fid in self.feeds.keys():
                cache_key = f"posts:{fid}"
                cached = await self.redis_client.get(cache_key)
                if cached:
                    all_posts.extend(json.loads(cached))
            return all_posts

    async def refresh_all_feeds(
        self,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, int]:
        """
        Refresh all RSS feeds.

        Args:
            session: Optional database session for persistence

        Returns:
            Dictionary mapping feed_id to post count
        """
        results = {}
        for feed_id in self.feeds.keys():
            posts = await self.fetch_and_cache_feed(feed_id, session=session)
            results[feed_id] = len(posts)
        return results

    def get_all_blogs(self) -> List[dict]:
        """Get all blog source configurations."""
        return list(self.feeds.values())

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime.

        Handles various RSS date formats.

        Args:
            date_str: Date string from RSS feed

        Returns:
            datetime object or None
        """
        if not date_str:
            return None

        # Try common formats
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # RFC 2822
            "%a, %d %b %Y %H:%M:%S %Z",  # RFC 2822 without numeric timezone
            "%Y-%m-%dT%H:%M:%S%z",       # ISO 8601
            "%Y-%m-%dT%H:%M:%SZ",        # ISO 8601 UTC
            "%Y-%m-%d %H:%M:%S",         # Simple format
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue

        return None

    async def get_stats(self) -> dict:
        """Get RSS service statistics."""
        return {
            "total_feeds": len(self.feeds),
            "redis_connected": self.redis_client is not None,
            "cache_ttl": settings.CACHE_TTL
        }


# Global instance
rss_service = RSSService()
