# InfoMatrix - 技术博客 RSS 聚合器

一个收集个人技术博客的 RSS 聚合应用，使用 FastAPI + TanStack Start 构建。

## 项目架构

```
InfoMatrix/
├── backend/                 # Python 后端 (Railway 部署)
│   ├── app/
│   │   ├── main.py         # FastAPI 应用入口
│   │   ├── routers/        # API 路由
│   │   │   ├── health.py   # 健康检查
│   │   │   ├── blogs.py    # 博客源管理
│   │   │   ├── posts.py    # 文章获取
│   │   │   └── featured.py # 精选文章
│   │   ├── models/         # 数据模型
│   │   │   ├── schemas.py  # Pydantic 模型
│   │   │   └── database.py # SQLAlchemy ORM
│   │   ├── services/       # 业务逻辑
│   │   │   ├── rss_service.py   # RSS 解析
│   │   │   └── db_service.py    # 数据库操作
│   │   └── config.py       # 配置文件
│   ├── requirements.txt
│   ├── railway.json        # Railway 配置
│   └── Dockerfile          # Docker 配置
│
├── frontend/               # React 前端 (Vercel 部署)
│   ├── app/
│   │   ├── routes/        # 文件路由
│   │   │   ├── __root.tsx    # 根布局
│   │   │   └── index.tsx     # 首页
│   │   ├── components/    # React 组件
│   │   │   ├── ui/           # shadcn/ui 组件
│   │   │   ├── Header.tsx    # 头部导航
│   │   │   ├── PostCard.tsx  # 文章卡片
│   │   │   └── FilterBar.tsx # 筛选栏
│   │   ├── services/
│   │   │   └── api.ts        # API 客户端
│   │   └── styles.css     # 全局样式
│   ├── public/            # 静态资源
│   │   └── matrix-white.svg
│   ├── package.json
│   ├── vite.config.ts     # Vite 配置
│   └── vercel.json        # Vercel 配置
│
└── README.md
```

## 技术栈

### 后端
- **FastAPI**: 现代异步 Python Web 框架
- **SQLAlchemy 2.0**: 异步 ORM
- **PostgreSQL**: 持久化存储（全文搜索）
- **Redis**: 高性能缓存层（可选，支持降级）
- **feedparser**: RSS/Atom 解析
- **httpx**: 异步 HTTP 客户端
- **Alembic**: 数据库迁移

### 前端
- **TanStack Start**: 全栈 React 框架（文件路由 + SSR）
- **React 19**: UI 框架
- **shadcn/ui**: 基于 Radix UI 的组件库
- **TailwindCSS v4**: 实用优先的 CSS 框架（OKLCH 配色）
- **Lucide React**: 图标库
- **Vite 7**: 快速的构建工具

## 部署平台

### Railway (后端)
- 免费额度: $5/月
- 包括: 512MB RAM, 0.5GB CPU
- 免费 PostgreSQL 插件
- 免费 Redis 插件（可选）

### Vercel (前端)
- 免费额度: 无限
- 包括: 100GB 带宽/月
- 自动 HTTPS
- 边缘网络 CDN

## 本地开发

### 前置要求

- **Python 3.9+** - 后端运行环境
- **Node.js 22+** - 前端运行环境（Vite 7.x 要求）
- **PostgreSQL** - 数据库（推荐 Docker）
- **Redis** - 缓存服务（可选，不安装会降级运行）

### 1. 克隆项目

```bash
git clone https://github.com/lance631/InfoMatrix.git
cd InfoMatrix
```

### 2. 启动 PostgreSQL（推荐 Docker）

```bash
docker run -d \
  --name infomatrix-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=infomatrix \
  -p 5432:5432 \
  postgres:16-alpine
```

### 3. 启动 Redis（可选）

```bash
docker run -d \
  --name infomatrix-redis \
  -p 6379:6379 \
  redis:alpine
```

验证 Redis 是否运行：
```bash
redis-cli ping  # 应返回 PONG
```

### 4. 后端设置

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和 Redis URL

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将运行在 [http://localhost:8000](http://localhost:8000)

查看 API 文档: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. 前端设置

打开新终端：

```bash
# 使用 nvm 切换到 Node.js 22+
nvm use 22

cd frontend

# 安装依赖（使用 pnpm）
pnpm install

# 配置环境变量
cp .env.example .env
# 开发环境留空即可，使用 Vite 代理

# 启动开发服务器
pnpm dev
```

前端将运行在 [http://localhost:3000](http://localhost:3000)

### 开发工作流

**推荐方式：使用 VSCode 分屏终端**

1. 保持 VSCode 窗口打开 `InfoMatrix` 目录
2. 创建分屏终端（`Cmd + Shift + 5`）
3. 左侧运行后端，右侧运行前端

```bash
# 终端 1 - 后端
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# 终端 2 - 前端
nvm use 22 && cd frontend && pnpm dev
```

### 环境变量配置

#### 后端 (.env)
```bash
# PostgreSQL 数据库
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/infomatrix

# Redis 缓存（可选）
REDIS_URL=redis://localhost:6379

# 缓存时间（秒）
CACHE_TTL=3600

# CORS 允许的源
CORS_ORIGINS=http://localhost:3000

# 服务器端口
PORT=8000
```

#### 前端 (.env)
```bash
# 开发环境留空，使用 Vite 代理
VITE_API_URL=

# 生产环境设置完整后端 URL
# VITE_API_URL=https://your-backend.railway.app/api
```

### 常见问题

**Q: Node.js 版本不兼容？**
A: 前端使用 Vite 7.x，需要 Node.js 20.19+ 或 22.12+。使用 nvm 切换版本：
```bash
nvm install 22
nvm use 22
```

**Q: PostgreSQL 连接失败？**
A: 确保 Docker 容器正在运行：
```bash
docker ps | grep postgres
```

**Q: Redis 连接失败？**
A: Redis 是可选的。不使用 Redis 时系统会降级为直接查询数据库，功能正常但性能略低。

**Q: 前端无法连接后端？**
A: 确认：
1. 后端正在运行（访问 http://localhost:8000/api/health）
2. Vite 代理配置正确
3. CORS 配置包含 `http://localhost:3000`

## 核心功能

### 文章聚合
- 自动获取 RSS/Atom 订阅源
- 幂等性设计（同一文章不重复）
- 支持手动和定时刷新

### 分类筛选
- 按博客分类筛选文章
- 支持多分类管理
- 动态筛选切换

### 精选文章
- 管理员精选周文章
- 支持编辑备注
- 按周归档展示

## API 端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/blogs` | 获取所有博客源 |
| GET | `/api/blogs/categories` | 获取分类列表 |
| GET | `/api/posts` | 获取文章列表（支持筛选） |
| POST | `/api/posts/refresh` | 手动刷新 RSS |
| GET | `/api/posts/stats` | 获取统计信息 |
| GET | `/api/posts/search` | 全文搜索文章 |
| GET | `/api/featured` | 获取精选周列表 |
| GET | `/api/featured/{week}` | 获取某周精选文章 |
| POST | `/api/featured` | 添加精选文章 |
| DELETE | `/api/featured/{id}` | 删除精选文章 |

## 部署

### Railway 部署后端

```bash
cd backend
railway login
railway init
railway up
```

在 Railway 控制台：
1. 添加 PostgreSQL 插件
2. 添加 Redis 插件（可选）
3. 配置环境变量
4. 获取后端 URL

### Vercel 部署前端

```bash
cd frontend
vercel login
vercel --prod
```

在 Vercel 控制台配置环境变量：
```
VITE_API_URL=https://your-backend.railway.app/api
```

更新 Railway 的 CORS 设置：
```
CORS_ORIGINS=https://your-frontend.vercel.app
```

## 许可证

MIT
