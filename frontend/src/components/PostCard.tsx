import type { Post } from '@/services/api'
import { Card, CardContent, CardFooter, CardHeader } from './ui/card'
import { Badge } from './ui/badge'
import { ExternalLink, Calendar } from 'lucide-react'

interface PostCardProps {
  post: Post
}

export default function PostCard({ post }: PostCardProps) {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No date'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <Card className="h-full flex flex-col hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between gap-2 mb-2">
          <Badge variant="secondary">{post.category}</Badge>
          {post.published && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Calendar className="w-3 h-3" />
              {formatDate(post.published)}
            </div>
          )}
        </div>
        <h3 className="text-lg font-semibold leading-tight line-clamp-2">
          {post.title}
        </h3>
        {post.blog_name && (
          <p className="text-sm text-muted-foreground mt-1">{post.blog_name}</p>
        )}
      </CardHeader>
      <CardContent className="flex-1">
        {post.summary && (
          <p className="text-sm text-muted-foreground line-clamp-3">
            {post.summary}
          </p>
        )}
      </CardContent>
      <CardFooter>
        <a
          href={post.link}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-sm font-medium text-primary hover:underline"
        >
          Read more <ExternalLink className="w-4 h-4" />
        </a>
      </CardFooter>
    </Card>
  )
}
