import { Post } from '@/services/api';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface PostCardProps {
  post: Post;
}

export function PostCard({ post }: PostCardProps) {
  const publishedAt = post.published
    ? formatDistanceToNow(new Date(post.published), {
        addSuffix: true,
        locale: zhCN,
      })
    : null;

  return (
    <article className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
      <div className="flex items-center gap-2 mb-2">
        <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs font-medium rounded">
          {post.category}
        </span>
        <span className="text-sm text-gray-500">{post.blog_name}</span>
      </div>

      <h2 className="text-xl font-semibold mb-2">
        <a
          href={post.link}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-primary-600 transition-colors"
        >
          {post.title}
        </a>
      </h2>

      <p
        className="text-gray-600 mb-4 line-clamp-2"
        dangerouslySetInnerHTML={{
          __html: post.summary.replace(/<[^>]*>/g, '').slice(0, 200) + '...',
        }}
      />

      <div className="flex items-center justify-between text-sm text-gray-500">
        {post.author && <span>{post.author}</span>}
        {publishedAt && <span>{publishedAt}</span>}
      </div>
    </article>
  );
}
