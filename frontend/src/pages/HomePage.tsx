import { useState, useMemo } from 'react';
import { usePosts, useCategories } from '@/hooks/useApi';
import { PostCard } from '@/components/PostCard';
import { FilterBar } from '@/components/FilterBar';
import { Header } from '@/components/Header';

export function HomePage() {
  const [filters, setFilters] = useState<{ category?: string; search?: string }>({});
  const { data: posts, isLoading, error } = usePosts(filters);
  const { data: categoriesData } = useCategories();

  const categories = categoriesData?.categories || [];

  const filteredPosts = useMemo(() => {
    if (!posts) return [];

    let filtered = posts;

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(
        (post) =>
          post.title.toLowerCase().includes(searchLower) ||
          post.summary.toLowerCase().includes(searchLower) ||
          post.blog_name.toLowerCase().includes(searchLower)
      );
    }

    return filtered;
  }, [posts, filters]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            错误: {error.message}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="container mx-auto px-4 py-8">
        <FilterBar categories={categories} onFilterChange={setFilters} />

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">加载中...</p>
          </div>
        ) : filteredPosts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">暂无文章</p>
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-600">
              共 {filteredPosts.length} 篇文章
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredPosts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
