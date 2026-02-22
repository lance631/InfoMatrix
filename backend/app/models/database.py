"""
SQLalchemy ORM models for PostgreSQL database.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index, DateTime, Date, func, UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Blog(Base):
    """Blog source model."""
    __tablename__ = "blogs"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    rss_url = Column(String, nullable=False, unique=True)  # RSS feed URL
    site_url = Column(String)  # Blog site URL for frontend navigation
    category = Column(String)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    posts = relationship("Post", back_populates="blog", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Blog(id={self.id}, name={self.name})>"


class Post(Base):
    """RSS post model."""
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True)
    blog_id = Column(UUID(as_uuid=True), ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False)
    summary = Column(Text)
    content = Column(Text)  # Full article content
    thumbnail = Column(String)  # Thumbnail image URL extracted from content
    author = Column(String)
    published_at = Column(DateTime(timezone=True))
    tsv = Column(TSVECTOR)  # Full-text search vector

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes and Constraints
    __table_args__ = (
        Index("idx_blog_id", "blog_id"),
        Index("idx_published_at", "published_at"),
        Index("idx_posts_tsv", "tsv", postgresql_using="gin"),
        # Unique constraint to prevent duplicate posts from same blog
        # This is modeled as a unique index instead of UniqueConstraint for flexibility
    )

    # Relationships
    blog = relationship("Blog", back_populates="posts")
    featured = relationship("FeaturedPost", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title})>"


class FeaturedPost(Base):
    """Featured post model for weekly selections."""
    __tablename__ = "featured_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    week_start = Column(Date, nullable=False)  # Week start date (e.g., 2025-02-17)
    editor_notes = Column(Text)  # Editor notes
    order_index = Column(Integer)  # Display order within the week
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes and Constraints
    __table_args__ = (
        Index("idx_featured_week", "week_start"),
    )

    # Relationships
    post = relationship("Post", back_populates="featured")

    def __repr__(self):
        return f"<FeaturedPost(id={self.id}, week_start={self.week_start}, post_id={self.post_id})>"
