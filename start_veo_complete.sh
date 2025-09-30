#!/bin/bash

# Veo 一鍵啟動腳本
# 自動啟動虛擬環境，清理舊進程，啟動服務器

echo "🚀 Veo 一鍵啟動腳本"
echo "===================="

# 設置腳本目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 工作目錄: $SCRIPT_DIR"

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 找不到虛擬環境，請先運行 setup_venv.sh"
    exit 1
fi

echo "🐍 啟動虛擬環境..."
source venv/bin/activate

# 檢查依賴包
echo "📦 檢查依賴包..."
python -c "import fastapi, uvicorn, google.auth, google.cloud.aiplatform" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少依賴包，正在安裝..."
    pip install fastapi uvicorn google-auth google-cloud-aiplatform
fi

# 清理舊進程
echo "🧹 清理舊進程..."
# 殺掉佔用端口的進程
lsof -tiTCP:8001 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true
lsof -tiTCP:8080 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true

# 殺掉相關的 Python 進程
pkill -f "uvicorn.*server:app" 2>/dev/null || true
pkill -f "http.server.*8080" 2>/dev/null || true

# 等待一下確保進程完全結束
sleep 2

echo "✅ 舊進程清理完成"

# 啟動 FastAPI 後端
echo "🔧 啟動 FastAPI 後端服務器 (端口 8001)..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# 等待後端啟動
sleep 3

# 檢查後端是否成功啟動
if ! curl -s http://localhost:8001/docs > /dev/null; then
    echo "❌ 後端啟動失敗"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ 後端啟動成功 (PID: $BACKEND_PID)"

# 啟動前端 HTTP 服務器
echo "🌐 啟動前端 HTTP 服務器 (端口 8080)..."
python3 -m http.server 8080 &
FRONTEND_PID=$!

# 等待前端啟動
sleep 2

echo "✅ 前端啟動成功 (PID: $FRONTEND_PID)"

echo ""
echo "🎉 所有服務啟動完成！"
echo "===================="
echo "📡 後端 API: http://localhost:8001"
echo "🌐 前端界面: http://localhost:8080/frontend_test.html"
echo "📊 API 文檔: http://localhost:8001/docs"
echo ""
echo "💡 測試提示:"
echo "   1. 在瀏覽器打開前端界面"
echo "   2. 設置簡單參數 (480p, 短提示詞)"
echo "   3. 點擊生成 - 一次成功！"
echo ""
echo "🛑 要停止服務，請按 Ctrl+C 或運行: kill $BACKEND_PID $FRONTEND_PID"

# 保存 PID 到文件（可選）
echo "$BACKEND_PID" > .backend_pid
echo "$FRONTEND_PID" > .frontend_pid

# 等待用戶中斷
trap "echo '🛑 正在停止服務...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; rm -f .backend_pid .frontend_pid; exit 0" INT TERM

# 保持腳本運行
wait