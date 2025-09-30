#!/bin/bash

# 🔍 0919TEST 環境驗證腳本
# 檢查所有必要檔案和設定是否完整

echo "🔍 Veo AI 環境驗證開始..."
echo "================================"

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
TOTAL=0

check_file() {
    TOTAL=$((TOTAL + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌${NC} $1 (缺失)"
    fi
}

check_dir() {
    TOTAL=$((TOTAL + 1))
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $1/"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌${NC} $1/ (缺失)"
    fi
}

check_executable() {
    TOTAL=$((TOTAL + 1))
    if [ -x "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 (可執行)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌${NC} $1 (不可執行)"
    fi
}

echo
echo "📋 檢查核心腳本文件..."
check_file "decode_previous_video.py"
check_file "setup_auth.py"
check_file "comprehensive_auth_test.py"
check_executable "quick_auth_setup.sh"
check_executable "start_veo.sh"

echo
echo "📁 檢查目錄結構..."
check_dir "venv"
check_dir "veo_videos"
check_dir "veo3_test_env"

echo
echo "📚 檢查說明文件..."
check_file "PROJECT_README.md"
check_file "AUTH_SETUP_GUIDE.md"
check_file "AUTOMATION_SUMMARY.md"
check_file "auth_config.py"

echo
echo "🧪 檢查測試腳本..."
check_file "structure_test.py"
check_file "comprehensive_test.py"
check_file "text_to_video.py"
check_file "image_to_video.py"

echo
echo "🔧 檢查環境..."
TOTAL=$((TOTAL + 1))
if command -v python >/dev/null 2>&1; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo -e "${GREEN}✅${NC} Python: $PYTHON_VERSION"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌${NC} Python 未安裝"
fi

# 檢查虛擬環境中的 Python
if [ -f "./venv/bin/python" ]; then
    TOTAL=$((TOTAL + 1))
    VENV_PYTHON_VERSION=$(./venv/bin/python --version 2>&1)
    echo -e "${GREEN}✅${NC} 虛擬環境 Python: $VENV_PYTHON_VERSION"
    PASSED=$((PASSED + 1))
fi

# 檢查 gcloud（可選）
if command -v gcloud >/dev/null 2>&1; then
    GCLOUD_VERSION=$(gcloud --version | head -1 2>&1)
    echo -e "${GREEN}✅${NC} Google Cloud CLI: $GCLOUD_VERSION"
else
    echo -e "${YELLOW}⚠️${NC} Google Cloud CLI 未安裝 (將由認證腳本處理)"
fi

echo
echo "================================"
echo -e "📊 驗證結果: ${GREEN}$PASSED${NC}/${TOTAL} 項檢查通過"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 環境驗證完全通過！${NC}"
    echo
    echo "🚀 您可以開始使用："
    echo "   ./start_veo.sh          # 一鍵啟動選單"
    echo "   ./quick_auth_setup.sh   # 快速認證設定"
    echo
elif [ $PASSED -gt $((TOTAL * 3 / 4)) ]; then
    echo -e "${YELLOW}⚠️ 環境基本完整，可以使用${NC}"
    echo
    echo "🔧 建議修復缺失項目後使用"
    echo
else
    echo -e "${RED}❌ 環境不完整，請檢查安裝${NC}"
    echo
    echo "🔧 建議重新設定環境"
    echo
fi

# 顯示目錄結構摘要
echo "📋 目錄結構摘要："
echo "   $(pwd)"
ls -la | grep "^d" | awk '{print "     📁 " $9}' | grep -v "^\s*📁 \.$" | grep -v "^\s*📁 \.\.$"
ls -la | grep "^-.*\.sh$" | awk '{print "     🔧 " $9}'
ls -la | grep "^-.*\.py$" | wc -l | awk '{print "     🐍 " $1 " Python 腳本"}'
ls -la | grep "^-.*\.md$" | wc -l | awk '{print "     📚 " $1 " 說明文件"}'

echo
echo "✨ Veo AI 環境驗證完成"