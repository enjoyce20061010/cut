#!/bin/bash

# Veo 停止服務腳本
# 用法: ./stop_veo.sh

echo "🛑 停止 Veo 服務..."

# 停止端口佔用進程
echo "🔧 停止端口 8001 和 8080 的進程..."
lsof -tiTCP:8001,8080 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true

# 停止相關的 Python 進程
echo "🐍 停止 Python 進程..."
pkill -f "uvicorn.*server:app" 2>/dev/null || true
pkill -f "http.server.*8080" 2>/dev/null || true

# 清理 PID 文件
rm -f .backend_pid .frontend_pid

echo "✅ 所有服務已停止"