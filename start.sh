#!/bin/bash

echo "🚀 InfoMatrix 快速启动脚本"
echo "================================"

# 检查是否已安装依赖
if [ ! -d "backend/venv" ]; then
    echo "📦 安装后端依赖..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "✅ 依赖安装完成！"
echo ""
echo "启动服务："
echo "1. 后端: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. 前端: cd frontend && npm run dev"
echo ""
echo "或者使用一个终端窗口运行后端，另一个运行前端"
