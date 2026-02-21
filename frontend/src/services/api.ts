/**
 * API service for communicating with the backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface Blog {
  id: string;
  name: string;
  url: string;
  category: string;
  description?: string;
}

export interface Post {
  id: string;
  blog_id: string;
  blog_name: string;
  title: string;
  link: string;
  summary: string | null;
  content: string | null;
  published: string | null;
  author: string | null;
  category: string;
}

export interface FeaturedPost {
  id: number;
  post_id: string;
  week_start: string;
  editor_notes: string | null;
  order_index: number;
  created_at: string;
  title: string;
  link: string;
  blog_name: string;
}

export interface RefreshResponse {
  message: string;
  results: Record<string, number>;
  timestamp: string;
}

export interface StatsResponse {
  total_blogs: number;
  total_posts: number;
  total_featured: number;
  posts_by_category: Record<string, number>;
  redis_connected: boolean;
  cache_ttl: number;
}

/**
 * Fetch all blogs
 */
export async function fetchBlogs(): Promise<Blog[]> {
  const response = await fetch(`${API_BASE_URL}/blogs`);
  if (!response.ok) throw new Error('Failed to fetch blogs');
  return response.json();
}

/**
 * Fetch blog categories
 */
export async function fetchCategories(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/blogs/categories`);
  if (!response.ok) throw new Error('Failed to fetch categories');
  const data = await response.json();
  return data.categories;
}

/**
 * Fetch posts with optional filters
 */
export async function fetchPosts(options?: {
  blog_id?: string;
  category?: string;
  limit?: number;
  offset?: number;
}): Promise<Post[]> {
  const params = new URLSearchParams();
  if (options?.blog_id) params.append('blog_id', options.blog_id);
  if (options?.category) params.append('category', options.category);
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());

  const response = await fetch(`${API_BASE_URL}/posts?${params}`);
  if (!response.ok) throw new Error('Failed to fetch posts');
  return response.json();
}

/**
 * Refresh RSS feeds
 */
export async function refreshFeeds(): Promise<RefreshResponse> {
  const response = await fetch(`${API_BASE_URL}/posts/refresh`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to refresh feeds');
  return response.json();
}

/**
 * Fetch statistics
 */
export async function fetchStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/posts/stats`);
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
}

/**
 * Search posts
 */
export async function searchPosts(query: string, limit = 20): Promise<Post[]> {
  const response = await fetch(`${API_BASE_URL}/posts/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  if (!response.ok) throw new Error('Failed to search posts');
  return response.json();
}

/**
 * Fetch featured weeks
 */
export async function fetchFeaturedWeeks(): Promise<Array<{ week_start: string; post_count: number }>> {
  const response = await fetch(`${API_BASE_URL}/featured`);
  if (!response.ok) throw new Error('Failed to fetch featured weeks');
  return response.json();
}

/**
 * Fetch featured posts for a specific week
 */
export async function fetchFeaturedPosts(week: string): Promise<Array<{
  week_start: string;
  posts: FeaturedPost[];
}>> {
  const response = await fetch(`${API_BASE_URL}/featured/${week}`);
  if (!response.ok) throw new Error('Failed to fetch featured posts');
  return [await response.json()]; // API returns single object, wrap in array for consistency
}

/**
 * Add post to featured
 */
export async function addFeaturedPost(data: {
  post_id: string;
  week_start: string;
  editor_notes?: string;
  order_index?: number;
}): Promise<FeaturedPost> {
  const response = await fetch(`${API_BASE_URL}/featured`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to add featured post');
  }
  return response.json();
}

/**
 * Remove post from featured
 */
export async function removeFeaturedPost(featuredId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/featured/${featuredId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to remove featured post');
}

/**
 * Check health status
 */
export async function fetchHealth(): Promise<{
  status: string;
  database: { status: string };
  redis: { status: string };
  rss: { status: string; total_feeds: number };
}> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) throw new Error('Failed to fetch health status');
  return response.json();
}
