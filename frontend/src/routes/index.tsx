import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { Loader2, AlertCircle } from 'lucide-react'

import PostCard from '@/components/PostCard'
import FilterBar from '@/components/FilterBar'
import { fetchPosts, fetchCategories } from '@/services/api'
import type { Post } from '@/services/api'

export const Route = createFileRoute('/')({
  component: HomePage,
  validateSearch: (search: Record<string, unknown>) => ({
    blog_id: (search.blog_id as string | undefined) || undefined,
  }),
  // Disable SSR for this route to avoid server-side API calls
  ssr: false,
})

function HomePage() {
  const navigate = useNavigate()
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [categories, setCategories] = useState<string[]>([])
  const [posts, setPosts] = useState<Post[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Get blog_id from URL search params using TanStack Router
  const { blog_id } = Route.useSearch()

  // Fetch data on mount
  useEffect(() => {
    async function loadData() {
      setIsLoading(true)
      setError(null)
      try {
        const [catsData, postsData] = await Promise.all([
          fetchCategories(),
          fetchPosts({ blog_id: blog_id || undefined }),
        ])
        setCategories(catsData)
        setPosts(postsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [blog_id])

  const handleBlogClear = () => {
    navigate({ to: '/', search: {} })
  }

  const filteredPosts = selectedCategory
    ? posts.filter((p) => p.category === selectedCategory)
    : posts

  return (
    <div className="min-h-screen bg-background">
      <FilterBar
        selectedBlog={blog_id || null}
        selectedCategory={selectedCategory}
        categories={categories}
        onBlogClear={handleBlogClear}
        onCategoryChange={setSelectedCategory}
      />

      <main className="container mx-auto px-4 py-6">
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            <span className="ml-3 text-muted-foreground">Loading posts...</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-3 p-4 bg-destructive/10 text-destructive rounded-lg">
            <AlertCircle className="w-5 h-5" />
            <p>Failed to load posts. Please try again.</p>
          </div>
        )}

        {!isLoading && !error && filteredPosts.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No posts found.</p>
          </div>
        )}

        {!isLoading && !error && filteredPosts.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPosts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
