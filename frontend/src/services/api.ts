const API_URL = import.meta.env.VITE_API_URL || '/api';

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
  summary: string;
  published?: string;
  author?: string;
  category: string;
}

export interface Stats {
  total_blogs: number;
  total_posts: number;
  redis_connected: boolean;
}

// 获取所有博客
export async function fetchBlogs(): Promise<Blog[]> {
  const response = await fetch(`${API_URL}/blogs`);
  if (!response.ok) throw new Error('Failed to fetch blogs');
  return response.json();
}

// 获取所有文章
export async function fetchPosts(params?: {
  blog_id?: string;
  category?: string;
  limit?: number;
}): Promise<Post[]> {
  const searchParams = new URLSearchParams();
  if (params?.blog_id) searchParams.set('blog_id', params.blog_id);
  if (params?.category) searchParams.set('category', params.category);
  if (params?.limit) searchParams.set('limit', params.limit.toString());

  const url = `${API_URL}/posts${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch posts');
  return response.json();
}

// 刷新RSS源
export async function refreshFeeds(): Promise<{ message: string; results: Record<string, number> }> {
  const response = await fetch(`${API_URL}/posts/refresh`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to refresh feeds');
  return response.json();
}

// 获取统计信息
export async function fetchStats(): Promise<Stats> {
  const response = await fetch(`${API_URL}/posts/stats`);
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
}

// 获取分类
export async function fetchCategories(): Promise<{ categories: string[] }> {
  const response = await fetch(`${API_URL}/blogs/categories`);
  if (!response.ok) throw new Error('Failed to fetch categories');
  return response.json();
}
