import { useStats, useRefreshFeeds } from '@/hooks/useApi';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

export function Header() {
  const { data: stats, isLoading } = useStats();
  const refreshMutation = useRefreshFeeds();

  const handleRefresh = () => {
    refreshMutation.mutate();
  };

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">InfoMatrix</h1>
            <p className="text-gray-600 mt-1">技术博客RSS聚合器</p>
          </div>

          <div className="flex items-center gap-4">
            {isLoading ? (
              <div className="text-gray-500">加载中...</div>
            ) : stats ? (
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>{stats.total_blogs} 个博客</span>
                <span>{stats.total_posts} 篇文章</span>
                {stats.redis_connected && (
                  <span className="text-green-600">● 在线</span>
                )}
              </div>
            ) : null}

            <button
              onClick={handleRefresh}
              disabled={refreshMutation.isPending}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {refreshMutation.isPending ? '刷新中...' : '刷新'}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
