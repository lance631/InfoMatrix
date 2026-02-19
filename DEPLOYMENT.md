# 部署指南

本文档详细介绍如何将 InfoMatrix 部署到 Railway（后端）和 Vercel（前端）。

## 前置准备

### 1. 安装必要工具
```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 安装 Vercel CLI
npm install -g vercel

# 确保 Python 和 Node.js 已安装
python --version  # Python 3.10+
node --version    # Node.js 18+
```

### 2. 注册账号
- Railway: https://railway.app/
- Vercel: https://vercel.com/

---

## 后端部署 (Railway)

### 步骤 1: 创建 Railway 项目

```bash
cd backend

# 登录 Railway
railway login

# 初始化项目
railway init
```

在浏览器中选择或创建一个新的 Railway 项目。

### 步骤 2: 配置环境变量

在 Railway 控制台中配置以下环境变量：

1. 进入项目设置 -> Variables
2. 添加以下变量：

```bash
REDIS_URL=redis://default:password@hostname:port
CACHE_TTL=3600
CORS_ORIGINS=https://your-domain.vercel.app
PORT=8000
```

**获取 Redis URL：**
- 在 Railway 项目中添加一个 Redis 插件
- 在 Redis 插件页面找到连接字符串

### 步骤 3: 部署

```bash
# 提交代码到 Git
git init
git add .
git commit -m "Initial commit"

# 推送到 GitHub（Railway 需要）
git remote add origin https://github.com/your-username/infomatrix.git
git push -u origin main

# 在 Railway 中连接 GitHub 仓库
# Railway 会自动检测并部署
```

### 步骤 4: 获取后端 URL

部署成功后，Railway 会提供一个 URL，例如：
```
https://infomatrix-backend.up.railway.app
```

**记下这个 URL，部署前端时需要用到。**

### 步骤 5: 验证部署

访问后端 API 文档：
```
https://your-backend.railway.app/docs
```

测试健康检查端点：
```bash
curl https://your-backend.railway.app/api/health
```

---

## 前端部署 (Vercel)

### 步骤 1: 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cd frontend
cp .env.example .env
```

编辑 `.env` 文件：

```bash
VITE_API_URL=https://your-backend.railway.app/api
```

### 步骤 2: 本地测试

```bash
# 安装依赖
npm install

# 本地运行测试
npm run dev
```

访问 http://localhost:5173 确保应用正常工作。

### 步骤 3: 部署到 Vercel

```bash
# 登录 Vercel
vercel login

# 部署（交互式）
vercel

# 或者一次性部署到生产环境
vercel --prod
```

### 步骤 4: 在 Vercel 控制台配置环境变量

1. 访问 Vercel 控制台
2. 进入项目 -> Settings -> Environment Variables
3. 添加：
   - Name: `VITE_API_URL`
   - Value: `https://your-backend.railway.app/api`
4. 重新部署项目

### 步骤 5: 配置自定义域名（可选）

1. 在 Vercel 项目设置中添加自定义域名
2. 更新 Railway 后端的 CORS_ORIGINS 环境变量，包含你的自定义域名

---

## 完整部署流程示例

### 1. 准备代码仓库

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: InfoMatrix RSS Aggregator"

# 推送到 GitHub
git remote add origin https://github.com/your-username/infomatrix.git
git push -u origin main
```

### 2. 部署后端

**方式 1: 使用 Railway CLI**

```bash
cd backend

railway login
railway init
railway up
```

**方式 2: 使用 Railway 控制台**

1. 访问 https://railway.app/
2. 点击 "New Project" -> "Deploy from GitHub repo"
3. 选择你的仓库
4. Railway 会自动检测 Python 项目并部署
5. 添加 Redis 插件
6. 配置环境变量
7. 等待部署完成

### 3. 部署前端

**方式 1: 使用 Vercel CLI**

```bash
cd frontend

vercel login
vercel
```

**方式 2: 使用 Vercel 控制台**

1. 访问 https://vercel.com/
2. 点击 "Add New" -> "Project"
3. 导入你的 GitHub 仓库
4. 配置项目设置：
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. 添加环境变量 `VITE_API_URL`
6. 点击 "Deploy"

---

## 监控和维护

### 后端监控 (Railway)

- 查看日志：Railway 控制台 -> Logs
- 查看指标：Railway 控制台 -> Metrics
- 查看部署历史：Railway 控制台 -> Deploys

### 前端监控 (Vercel)

- 查看构建日志：Vercel 控制台 -> Deployments
- 查看分析：Vercel 控制台 -> Analytics
- 查看函数执行：Vercel 控制台 -> Functions

### 更新应用

```bash
# 修改代码后
git add .
git commit -m "Update feature"
git push

# Railway 和 Vercel 会自动检测并部署新版本
```

---

## 故障排除

### 常见问题

**1. CORS 错误**
- 确保后端 `CORS_ORIGINS` 包含前端域名
- 检查前端 `VITE_API_URL` 是否正确

**2. Redis 连接失败**
- 检查 `REDIS_URL` 格式是否正确
- 确保 Redis 插件已在 Railway 中添加并启动

**3. 前端无法访问 API**
- 检查后端是否正常运行
- 验证 `VITE_API_URL` 是否包含 `/api` 后缀
- 检查浏览器控制台的网络请求

**4. 构建失败**
- 检查依赖版本是否正确
- 本地运行 `npm run build` 测试
- 查看构建日志定位问题

---

## 成本估算

### Railway (后端)
- 免费额度: $5/月
- 包括: 512MB RAM, 0.5GB CPU
- 免费Redis: 10,000条命令/月
- 超出后按使用量计费

### Vercel (前端)
- 免费额度: 无限
- 包括:
  - 100GB 带宽/月
  - 无限部署
  - 自动HTTPS
  - 全球CDN

---

## 下一步优化

### 1. 添加更多功能
- 搜索功能
- 收藏文章
- 阅读历史
- 邮件订阅

### 2. 性能优化
- 实现增量刷新
- 添加服务端渲染 (SSR)
- 实现图片懒加载

### 3. 监控和告警
- 添加错误监控 (Sentry)
- 设置性能监控
- 配置告警通知

### 4. 测试
- 添加单元测试
- 添加集成测试
- 配置 CI/CD

---

## 有用的链接

- Railway 文档: https://docs.railway.app/
- Vercel 文档: https://vercel.com/docs
- FastAPI 文档: https://fastapi.tiangolo.com/
- React Query 文档: https://tanstack.com/query/latest
- Vite 文档: https://vitejs.dev/
