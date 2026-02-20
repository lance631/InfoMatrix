"""Update schema to use UUID and add full-text search

Revision ID: 2ecb2ee290d4
Revises: 1d768a7a2916
Create Date: 2026-02-19 23:45:39.788094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2ecb2ee290d4'
down_revision: Union[str, None] = '1d768a7a2916'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # DEV ONLY: destructive migration
    op.drop_table('featured_posts', if_exists=True)
    op.drop_table('posts', if_exists=True)
    op.drop_table('blogs', if_exists=True)

    # blogs
    op.create_table(
        'blogs',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('rss_url', sa.String(), nullable=False, unique=True),
        sa.Column('site_url', sa.String()),
        sa.Column('category', sa.String()),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # posts
    op.create_table(
        'posts',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('blog_id', sa.UUID(), sa.ForeignKey('blogs.id', ondelete='CASCADE')),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('link', sa.String(), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('content', sa.Text()),
        sa.Column('author', sa.String()),
        sa.Column('published_at', sa.DateTime(timezone=True)),
        sa.Column('tsv', postgresql.TSVECTOR()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('blog_id', 'link', name='uq_blog_link'),
    )
    op.create_index('idx_posts_blog', 'posts', ['blog_id'])
    op.create_index('idx_posts_published', 'posts', ['published_at'])
    op.create_index('idx_posts_tsv', 'posts', ['tsv'], postgresql_using='gin')

    # featured_posts
    op.create_table(
        'featured_posts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('post_id', sa.UUID(), sa.ForeignKey('posts.id', ondelete='CASCADE')),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('editor_notes', sa.Text()),
        sa.Column('order_index', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('week_start', 'post_id', name='uq_week_post'),
    )

    op.create_index('idx_featured_week', 'featured_posts', ['week_start'])

def downgrade() -> None:
    raise RuntimeError("Downgrade not supported due to destructive migration")
