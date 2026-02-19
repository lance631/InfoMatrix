# CLAUDE.md

This file provides authoritative guidance to Claude Code (claude.ai/code) when working in this repository. Claude should follow the architetural intent,constraints,and conventions described here.

## Project Overview

InfoMatrix is a technical blog RSS aggregator built with FastAPI (backend) and React + TanStack Query (frontend). The app fetches RSS feeds from technical blogs, aggregates them, and presents them in a unified interface.

## Architecture

### Backend (FastAPI)

- **Entry point**: `backend/app/main.py`
- **Configuration**: `backend/app/config.py` (uses `pydantic-settings` for env vars)
- **Router structure**:
  - `routers/health.py` - Health check endpoint
  - `routers/blogs.py` - Blog list and categories
  - `routers/posts.py` - Post retrieval and refresh
- **Services**: `services/rss_service.py` - RSS fetching and caching with Redis
- **Models**: `models/schemas.py` - Pydantic models for request/response validation

Key patterns:

- Uses async/await throughout with `httpx` for HTTP requests
- Redis caching with configurable TTL (default 1 hour)
- CORS configured via `CORS_ORIGINS` in settings (local dev + env var)
- RSS sources defined in `config.py` as `RSS_FEEDS` list

### Frontend (React + Vite)

- **Entry point**: `frontend/src/main.tsx`
- **Routing**: Uses `react-router-dom` (not TanStack Router as mentioned in README)
- **Data fetching**: TanStack Query with 1-minute stale time
- **Styling**: TailwindCSS
- **Path aliases**: `@/` maps to `frontend/src/` (configured in vite.config.ts)

Component structure:

- `components/` - Reusable UI components (Header, PostCard, FilterBar)
- `pages/` - Page-level components (HomePage)
- `hooks/` - Custom React hooks
- `services/` - API client layer

## Development Commands

### Backend

```bash
cd backend

# First time setup (if venv doesn't exist)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

### Quick Start (Both)

```bash
# From project root - installs deps if needed
bash start.sh

# Then run backend and frontend in separate terminals:
# Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload
# Terminal 2: cd frontend && npm run dev
```

## Environment Variables

### Backend (.env in backend/ or environment)

- `REDIS_URL` - Redis connection string (default: redis://localhost:6379)
- `CACHE_TTL` - Cache TTL in seconds (default: 3600)
- `CORS_ORIGINS` - Comma-separated list of allowed frontend origins

### Frontend (.env in frontend/)

- `VITE_API_URL` - Backend API base URL (e.g., http://localhost:8000/api)

## API Endpoints

- `GET /api/health` - Health check and Redis status
- `GET /api/blogs` - Get all registered blog sources
- `GET /api/blogs/categories` - Get unique categories
- `GET /api/posts` - Get all posts, optionally filtered by `blog_id` or `category`
- `GET /api/posts/refresh` - Manually trigger RSS feed refresh

## Deployment

- **Backend**: Railway (uses `railway.json` config, Dockerfile for containerization)
- **Frontend**: Vercel (uses `vercel.json` config)

See DEPLOYMENT.md for detailed deployment instructions.

## Key Implementation Details

- RSS feeds are initialized on app startup via the startup_event in main.py
- The RSS service maintains cached data in Redis to avoid fetching on every request
- Frontend uses TanStack Query's built-in caching (1-minute stale time)
- All API routes are prefixed with `/api`
- CORS must be configured to allow the frontend origin in production
