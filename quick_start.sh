#!/bin/bash

# Veo 快速啟動腳本 (簡化版)
# 用法: ./quick_start.sh

cd "$(dirname "$0")"

echo "🚀 啟動 Veo 服務..."

# 啟動虛擬環境
source venv/bin/activate

# 清理舊進程
echo "🧹 清理舊進程..."
lsof -tiTCP:8001,8080 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true
pkill -f "uvicorn.*server:app" 2>/dev/null || true
pkill -f "http.server.*8080" 2>/dev/null || true
sleep 2

# 啟動服務器
echo "🔧 啟動後端..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /dev/null 2>&1 &
sleep 3

echo "🌐 啟動前端..."
python3 -m http.server 8080 > /dev/null 2>&1 &
sleep 2

echo "✅ 完成！"
echo "🌐 前端: http://localhost:8080/frontend_test.html"
echo "📡 後端: http://localhost:8001"