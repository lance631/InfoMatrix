import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchBlogs, fetchPosts, refreshFeeds, fetchStats, fetchCategories } from '@/services/api';

export function useBlogs() {
  return useQuery({
    queryKey: ['blogs'],
    queryFn: fetchBlogs,
  });
}

export function usePosts(params?: { blog_id?: string; category?: string; limit?: number }) {
  return useQuery({
    queryKey: ['posts', params],
    queryFn: () => fetchPosts(params),
  });
}

export function useRefreshFeeds() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: refreshFeeds,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
}

export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    refetchInterval: 60000, // 每分钟刷新一次
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
  });
}
