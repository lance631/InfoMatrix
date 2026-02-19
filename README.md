# InfoMatrix - 技术博客RSS聚合器

一个收集个人技术博客的RSS聚合应用，使用FastAPI + TanStack构建。

## 项目架构

```
InfoMatrix/
├── backend/                 # Python后端 (Railway部署)
│   ├── app/
│   │   ├── main.py         # FastAPI应用入口
│   │   ├── routers/        # API路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # RSS解析和缓存服务
│   │   └── config.py       # 配置文件
│   ├── requirements.txt
│   ├── railway.json        # Railway配置
│   └── Dockerfile          # Docker配置
│
├── frontend/               # React前端 (Vercel部署)
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面组件
│   │   ├── hooks/          # 自定义hooks
│   │   └── main.tsx        # 入口文件
│   ├── package.json
│   ├── vite.config.ts
│   └── vercel.json         # Vercel配置
│
└── README.md
```

## 技术栈

### 后端
- **FastAPI**: 现代Python Web框架
- **feedparser**: RSS/Atom解析
- **httpx**: 异步HTTP客户端
- **Redis**: RSS缓存（Railway免费Redis）
- **uvicorn**: ASGI服务器

### 前端
- **React 18**: UI框架
- **TanStack Query**: 数据获取和缓存
- **TanStack Router**: 路由管理
- **Vite**: 构建工具
- **TailwindCSS**: 样式框架

## 部署平台

### Railway (后端)
- 免费额度: $5/月
- 包括: 512MB RAM, 0.5GB CPU
- 免费Redis: 10,000条命令/月

### Vercel (前端)
- 免费额度: 无限
- 包括: 100GB带宽/月
- 自动HTTPS

## 本地开发

### 前置要求

- **Python 3.9+** - 后端运行环境
- **Node.js 18+** - 前端运行环境
- **Redis** - 缓存服务（可选，不安装会降级运行）

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd InfoMatrix
```

### 2. 安装 Redis（可选但推荐）

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

**Docker (推荐):**
```bash
docker run -d -p 6379:6379 redis:alpine
```

验证 Redis 是否运行：
```bash
redis-cli ping  # 应返回 PONG
```

### 3. 后端设置

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制示例文件）
cp .env.example .env
# 编辑 .env 文件，配置 Redis URL 和其他设置

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将运行在 [http://localhost:8000](http://localhost:8000)

查看 API 文档: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. 前端设置

打开新终端：

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量（复制示例文件）
cp .env.example .env
# 编辑 .env 文件，设置 VITE_API_URL

# 启动开发服务器
npm run dev
```

前端将运行在 [http://localhost:5173](http://localhost:5173)

### 5. 使用启动脚本（可选）

项目提供了快速启动脚本：

```bash
chmod +x start.sh
./start.sh
```

### 开发工作流

**推荐方式：使用 VSCode 分屏终端**

1. 保持当前 VSCode 窗口打开 `InfoMatrix` 目录
2. 创建分屏终端（`Cmd + Shift + 5` 或点击终端右上角分屏图标）
3. 左侧终端运行后端，右侧终端运行前端

**启动命令：**

```bash
# 终端 1 - 后端
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# 终端 2 - 前端
cd frontend && npm run dev
```

### 环境变量配置

#### 后端 (.env)
```bash
# Redis配置（使用 Docker 运行的 Redis）
REDIS_URL=redis://localhost:6379

# 缓存时间（秒）
CACHE_TTL=3600

# CORS允许的源（逗号分隔）
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 端口
PORT=8000
```

#### 前端 (.env)
```bash
# 开发环境可以使用 Vite 代理，留空即可
VITE_API_URL=

# 生产环境需要设置完整的后端URL
# VITE_API_URL=https://your-backend.railway.app/api
```

### 常见问题

**Q: Redis 连接失败怎么办？**
A: 可以不使用 Redis 运行，系统会降级为直接获取 RSS，但性能会降低。建议使用 Docker 快速启动 Redis：
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Q: 前端无法连接后端？**
A: 确保：
1. 后端服务正在运行（访问 http://localhost:8000/api/health）
2. 前端 .env 配置正确
3. 检查 CORS 配置是否包含前端地址

## 部署步骤

### 1. Railway部署后端
```bash
cd backend
railway login
railway init
railway up
```

### 2. Vercel部署前端
```bash
cd frontend
vercel login
vercel --prod
```

## 环境变量

### 后端 (.env)
```
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
CORS_ORIGINS=https://your-domain.vercel.app
```

### 前端 (.env)
```
VITE_API_URL=https://your-backend.railway.app
```

## API端点

- `GET /api/blogs` - 获取所有博客列表
- `GET /api/posts` - 获取聚合文章
- `GET /api/posts?blog_id=xxx` - 获取特定博客文章
- `GET /api/refresh` - 刷新RSS源
- `GET /api/health` - 健康检查

## 许可证

MIT
