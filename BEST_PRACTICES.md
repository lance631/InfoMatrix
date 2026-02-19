# 开发最佳实践

## 项目规范

### 代码结构

#### 后端结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   ├── routers/             # API路由
│   │   ├── health.py        # 健康检查
│   │   ├── blogs.py         # 博客相关
│   │   └── posts.py         # 文章相关
│   ├── models/              # 数据模型
│   │   └── schemas.py       # Pydantic模型
│   └── services/            # 业务逻辑
│       └── rss_service.py   # RSS服务
├── requirements.txt
└── railway.json
```

#### 前端结构
```
frontend/
├── src/
│   ├── components/          # React组件
│   │   ├── Header.tsx
│   │   ├── PostCard.tsx
│   │   └── FilterBar.tsx
│   ├── pages/               # 页面组件
│   │   └── HomePage.tsx
│   ├── hooks/               # 自定义Hooks
│   │   └── useApi.ts
│   ├── services/            # API服务
│   │   └── api.ts
│   ├── utils/               # 工具函数
│   ├── App.tsx              # 应用根组件
│   ├── main.tsx             # 应用入口
│   └── index.css            # 全局样式
├── index.html
├── vite.config.ts
└── package.json
```

### 命名规范

#### Python
- 文件名: 小写下划线 (rss_service.py)
- 类名: 大驼峰 (RSSService)
- 函数/变量: 小写下划线 (fetch_posts)
- 常量: 大写下划线 (CACHE_TTL)

#### TypeScript/React
- 文件名: 大驼峰 (PostCard.tsx)
- 组件名: 大驼峰 (PostCard)
- 变量/函数: 小驼峰 (fetchPosts)
- 常量: 大写下划线 (API_URL)
- Hooks: use前缀 (useApi)

### API 设计规范

#### RESTful API
```
GET    /api/blogs           # 获取所有博客
GET    /api/blogs/categories # 获取分类
GET    /api/posts           # 获取文章列表
POST   /api/posts/refresh   # 刷新RSS源
GET    /api/posts/stats     # 获取统计
GET    /api/health          # 健康检查
```

#### 响应格式
```json
{
  "data": { ... },
  "error": null
}
```

## 性能优化

### 后端优化

1. **使用缓存**
   - Redis缓存RSS内容
   - 设置合理的TTL (1小时)
   - 实现增量刷新

2. **异步处理**
   - 使用httpx异步HTTP客户端
   - 非阻塞I/O操作
   - 并发获取RSS源

3. **数据库优化**
   - 使用索引
   - 分页查询
   - 避免N+1查询

### 前端优化

1. **使用 TanStack Query**
   - 自动缓存和重验证
   - 乐观更新
   - 并行请求

2. **代码分割**
   ```ts
   const HomePage = lazy(() => import('./pages/HomePage'));
   ```

3. **图片优化**
   - 使用懒加载
   - 响应式图片
   - WebP格式

4. **构建优化**
   - Tree shaking
   - 压缩代码
   - CDN加速

## 安全最佳实践

### 后端安全

1. **环境变量**
   - 敏感信息使用环境变量
   - 不要提交 .env 文件
   - 使用 .env.example 模板

2. **CORS配置**
   - 只允许可信域名
   - 不要使用 `*` 通配符
   - 验证 Origin 头

3. **输入验证**
   - 使用 Pydantic 验证
   - 限制请求大小
   - 过滤恶意内容

4. **速率限制**
   - 实现 API 速率限制
   - 防止滥用
   - 使用 Redis 存储

### 前端安全

1. **XSS 防护**
   - 使用 React 的 JSX 自动转义
   - 避免使用 dangerouslySetInnerHTML
   - CSP 策略

2. **HTTPS**
   - 使用 Vercel 自动 HTTPS
   - 强制重定向到 HTTPS

3. **环境变量**
   - 使用 VITE_ 前缀
   - 不要在前端存储敏感信息

## 错误处理

### 后端错误处理

```python
from fastapi import HTTPException, status

@router.get("/posts/{post_id}")
async def get_post(post_id: str):
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post
```

### 前端错误处理

```tsx
const { data, error, isLoading } = usePosts();

if (error) {
  return <ErrorDisplay error={error} />;
}

if (isLoading) {
  return <LoadingSpinner />;
}
```

## 测试策略

### 后端测试

```python
# tests/test_api.py
from fastapi.testclient import TestClient

def test_get_blogs():
    client = TestClient(app)
    response = client.get("/api/blogs")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

### 前端测试

```tsx
// tests/PostCard.test.tsx
import { render, screen } from '@testing-library/react';
import { PostCard } from './PostCard';

test('renders post title', () => {
  const post = { /* ... */ };
  render(<PostCard post={post} />);
  expect(screen.getByText(post.title)).toBeInTheDocument();
});
```

## Git 工作流

### 分支策略

```
main          # 生产环境
  └── develop # 开发环境
      └── feature/*  # 功能分支
      └── fix/*      # 修复分支
```

### Commit 规范

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 构建/工具变动
```

示例：
```bash
git commit -m "feat: 添加文章搜索功能"
git commit -m "fix: 修复RSS解析错误"
```

## 监控和日志

### 后端监控

1. **健康检查**
   - `/api/health` 端点
   - 检查 Redis 连接
   - 返回基本统计

2. **日志记录**
   ```python
   import logging
   logger = logging.getLogger(__name__)

   logger.info("RSS feed refreshed")
   logger.error(f"Failed to fetch feed: {e}")
   ```

3. **性能监控**
   - 记录 API 响应时间
   - 监控缓存命中率
   - 追踪错误率

### 前端监控

1. **错误边界**
   ```tsx
   class ErrorBoundary extends React.Component {
     static getDerivedStateFromError(error) {
       return { hasError: true };
     }
   }
   ```

2. **性能监控**
   - Web Vitals
   - API 响应时间
   - 页面加载时间

## CI/CD

### GitHub Actions 示例

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      - name: Test Frontend
        run: |
          cd frontend
          npm install
          npm test
          npm run build
```

## 文档

### 代码文档

```python
def fetch_and_cache_feed(blog_id: str) -> List[dict]:
    """
    获取并缓存RSS源

    Args:
        blog_id: 博客ID

    Returns:
        文章列表

    Raises:
        HTTPException: 当RSS源无法访问时
    """
```

```tsx
/**
 * 文章卡片组件
 * @param post - 文章数据
 * @returns JSX.Element
 */
export function PostCard({ post }: PostCardProps) {
  // ...
}
```

### API 文档

1. 使用 FastAPI 自动生成的 Swagger UI
2. 访问 `/docs` 查看交互式文档
3. 使用 Redoc (`/redoc`) 查看备用文档

## 开发工作流

### 日常开发

1. **开始新功能**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **开发**
   - 编写代码
   - 运行测试
   - 本地验证

3. **提交**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin feature/new-feature
   ```

4. **代码审查**
   - 创建 Pull Request
   - 请求审查
   - 修改反馈

5. **合并**
   - 合并到 develop
   - 删除功能分支

### 发布流程

1. **更新版本**
   - 更新 package.json
   - 更新 CHANGELOG

2. **创建发布分支**
   ```bash
   git checkout -b release/v1.0.0
   ```

3. **部署到生产**
   - 合并到 main
   - 触发自动部署

4. **标记版本**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

## 有用的资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [TanStack Query 文档](https://tanstack.com/query/latest)
- [Vite 文档](https://vitejs.dev/)
- [Railway 文档](https://docs.railway.app/)
- [Vercel 文档](https://vercel.com/docs)
- [Python 最佳实践](https://docs.python-guide.org/)
- [React 最佳实践](https://react.dev/learn)
