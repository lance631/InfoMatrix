"""
Database service for CRUD operations.
All database access must go through this service layer.
"""
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert
from app.models.database import Blog, Post, FeaturedPost


# ============================================================================
# Blog Operations
# ============================================================================

async def get_blogs(
    session: AsyncSession,
    category: Optional[str] = None
) -> List[Blog]:
    """Get all blogs, optionally filtered by category."""
    query = select(Blog)
    if category:
        query = query.where(Blog.category == category)
    query = query.order_by(Blog.name)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_blog_by_id(session: AsyncSession, blog_id: uuid.UUID) -> Optional[Blog]:
    """Get a single blog by ID."""
    result = await session.execute(select(Blog).where(Blog.id == blog_id))
    return result.scalars().first()


async def get_blog_by_rss_url(session: AsyncSession, rss_url: str) -> Optional[Blog]:
    """Get a blog by RSS URL."""
    result = await session.execute(select(Blog).where(Blog.rss_url == rss_url))
    return result.scalars().first()


async def create_blog_if_not_exists(
    session: AsyncSession,
    blog_id: uuid.UUID,
    name: str,
    rss_url: str,
    category: Optional[str] = None,
    site_url: Optional[str] = None,
    description: Optional[str] = None
) -> Blog:
    """Create a blog if it doesn't exist, otherwise update and return existing."""
    blog = await get_blog_by_id(session, blog_id)
    if blog:
        # Update existing blog
        blog.name = name
        blog.rss_url = rss_url
        blog.category = category
        blog.site_url = site_url
        blog.description = description
        blog.updated_at = datetime.utcnow()
    else:
        # Create new blog
        blog = Blog(
            id=blog_id,
            name=name,
            rss_url=rss_url,
            category=category,
            site_url=site_url,
            description=description
        )
        session.add(blog)
    await session.commit()
    await session.refresh(blog)
    return blog


async def get_categories(session: AsyncSession) -> List[str]:
    """Get all unique blog categories."""
    result = await session.execute(
        select(Blog.category).where(Blog.category.isnot(None)).distinct().order_by(Blog.category)
    )
    return [row[0] for row in result.all() if row[0]]


# ============================================================================
# Post Operations
# ============================================================================

async def get_posts(
    session: AsyncSession,
    blog_id: Optional[uuid.UUID] = None,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Post]:
    """
    Get posts with optional filters.

    Args:
        session: Async database session
        blog_id: Filter by blog ID
        category: Filter by blog category (requires JOIN)
        limit: Max number of posts to return
        offset: Number of posts to skip

    Returns:
        List of Post objects with blog relationship loaded
    """
    query = select(Post).options(selectinload(Post.blog)).join(Blog)

    if blog_id:
        query = query.where(Post.blog_id == blog_id)
    if category:
        query = query.where(Blog.category == category)

    query = query.order_by(desc(Post.published_at)).limit(limit).offset(offset)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_post_by_id(session: AsyncSession, post_id: uuid.UUID) -> Optional[Post]:
    """Get a single post by ID."""
    result = await session.execute(
        select(Post).where(Post.id == post_id)
    )
    return result.scalars().first()


async def get_post_by_link(session: AsyncSession, blog_id: uuid.UUID, link: str) -> Optional[Post]:
    """Get a post by blog ID and link."""
    result = await session.execute(
        select(Post).where(and_(Post.blog_id == blog_id, Post.link == link))
    )
    return result.scalars().first()


async def upsert_post(
    session: AsyncSession,
    post_id: uuid.UUID,
    blog_id: uuid.UUID,
    title: str,
    link: str,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    thumbnail: Optional[str] = None,
    author: Optional[str] = None,
    published_at: Optional[datetime] = None
) -> Post:
    """
    Insert or update a post.

    Uses PostgreSQL ON CONFLICT for idempotent upsert.
    The unique constraint (blog_id, link) prevents duplicates.
    """
    # Check if post exists
    existing = await get_post_by_link(session, blog_id, link)

    if existing:
        # Update existing post
        existing.title = title
        existing.summary = summary
        existing.content = content
        existing.thumbnail = thumbnail
        existing.author = author
        existing.published_at = published_at
        existing.updated_at = datetime.utcnow()
        await session.commit()
        # Update the tsv column
        await update_post_tsv(session, post_id)
        await session.refresh(existing)
        return existing
    else:
        # Create new post
        post = Post(
            id=post_id,
            blog_id=blog_id,
            title=title,
            link=link,
            summary=summary,
            content=content,
            thumbnail=thumbnail,
            author=author,
            published_at=published_at
        )
        session.add(post)
        await session.commit()
        # Update the tsv column
        await update_post_tsv(session, post_id)
        await session.refresh(post)
        return post


async def search_posts(
    session: AsyncSession,
    query: str,
    limit: int = 20
) -> List[Post]:
    """
    Full-text search using PostgreSQL tsvector.

    Args:
        session: Async database session
        query: Search query (supports PostgreSQL tsquery syntax)
        limit: Max number of results

    Returns:
        List of matching posts ordered by relevance
    """
    # Use plainto_tsquery for simple query parsing
    from sqlalchemy import text

    sql = text("""
        SELECT id, blog_id, title, link, summary, author, published_at,
               ts_rank_cd(tsv, plainto_tsquery('english', :query)) as rank
        FROM posts
        WHERE tsv @@ plainto_tsquery('english', :query)
        ORDER BY rank DESC
        LIMIT :limit
    """)

    result = await session.execute(sql, {"query": query, "limit": limit})
    rows = result.all()

    # Fetch full Post objects for the IDs
    post_ids = [row[0] for row in rows]
    if not post_ids:
        return []

    posts_result = await session.execute(
        select(Post).options(selectinload(Post.blog)).where(Post.id.in_(post_ids))
    )
    posts = {post.id: post for post in posts_result.scalars().all()}

    # Return posts in the same order as the search results
    return [posts[pid] for pid in post_ids if pid in posts]


async def update_post_tsv(session: AsyncSession, post_id: uuid.UUID) -> None:
    """Update the full-text search vector for a post."""
    from sqlalchemy import text

    sql = text("""
        UPDATE posts
        SET tsv = to_tsvector('english',
            coalesce(title, '') || ' ' ||
            coalesce(summary, '') || ' ' ||
            coalesce(content, '')
        )
        WHERE id = :post_id
    """)

    await session.execute(sql, {"post_id": post_id})
    await session.commit()


# ============================================================================
# Featured Post Operations
# ============================================================================

async def get_featured_posts(
    session: AsyncSession,
    week_start: Optional[date] = None
) -> List[FeaturedPost]:
    """
    Get featured posts, optionally filtered by week.

    Args:
        session: Async database session
        week_start: Filter by week start date (YYYY-MM-DD)

    Returns:
        List of FeaturedPost objects with post and blog relationships loaded
    """
    # Eager load post.blog relationship (nested)
    query = select(FeaturedPost).options(
        selectinload(FeaturedPost.post).selectinload(Post.blog)
    )

    if week_start:
        query = query.where(FeaturedPost.week_start == week_start)

    query = query.order_by(FeaturedPost.week_start.desc(), FeaturedPost.order_index)

    result = await session.execute(query)
    return list(result.scalars().all())


async def add_featured_post(
    session: AsyncSession,
    post_id: uuid.UUID,
    week_start: date,
    editor_notes: Optional[str] = None,
    order_index: Optional[int] = None
) -> FeaturedPost:
    """
    Add a post to featured.

    Args:
        session: Async database session
        post_id: UUID of the post to feature
        week_start: Week start date
        editor_notes: Optional editor notes
        order_index: Display order within the week

    Returns:
        Created FeaturedPost object

    Raises:
        ValueError: If post is already featured for this week
    """
    # Check if already featured
    existing = await session.execute(
        select(FeaturedPost).where(
            and_(FeaturedPost.post_id == post_id, FeaturedPost.week_start == week_start)
        )
    )
    if existing.scalars().first():
        raise ValueError("Post is already featured for this week")

    # Get max order_index for this week if not provided
    if order_index is None:
        max_order = await session.execute(
            select(func.coalesce(func.max(FeaturedPost.order_index), 0))
            .where(FeaturedPost.week_start == week_start)
        )
        order_index = max_order.scalar() + 1

    featured = FeaturedPost(
        post_id=post_id,
        week_start=week_start,
        editor_notes=editor_notes,
        order_index=order_index
    )
    session.add(featured)
    await session.commit()
    await session.refresh(featured)
    return featured


async def remove_featured_post(session: AsyncSession, featured_id: int) -> bool:
    """
    Remove a post from featured.

    Args:
        session: Async database session
        featured_id: ID of the featured post entry

    Returns:
        True if removed, False if not found
    """
    result = await session.execute(
        select(FeaturedPost).where(FeaturedPost.id == featured_id)
    )
    featured = result.scalars().first()

    if featured:
        await session.delete(featured)
        await session.commit()
        return True
    return False


async def get_featured_weeks(session: AsyncSession) -> List[date]:
    """Get all weeks that have featured posts."""
    result = await session.execute(
        select(FeaturedPost.week_start)
        .distinct()
        .order_by(FeaturedPost.week_start.desc())
    )
    return [row[0] for row in result.all()]


# ============================================================================
# Statistics
# ============================================================================

async def get_stats(session: AsyncSession) -> Dict[str, Any]:
    """Get database statistics."""
    blog_count = await session.execute(select(func.count(Blog.id)))
    post_count = await session.execute(select(func.count(Post.id)))
    featured_count = await session.execute(select(func.count(FeaturedPost.id)))

    # Count posts by category
    category_counts = await session.execute(
        select(Blog.category, func.count(Post.id))
        .join(Post, Blog.id == Post.blog_id)
        .group_by(Blog.category)
        .order_by(func.count(Post.id).desc())
    )

    return {
        "total_blogs": blog_count.scalar(),
        "total_posts": post_count.scalar(),
        "total_featured": featured_count.scalar(),
        "posts_by_category": {row[0] or "Uncategorized": row[1] for row in category_counts.all()}
    }
