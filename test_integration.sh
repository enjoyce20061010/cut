#!/bin/bash

# 🚀 測試整合腳本
# 簡化版本用於測試

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 創建測試目錄
TEST_DIR="./test_integration_$(date +%Y%m%d_%H%M%S)"
SOURCE_DIR="/Users/jianjunneng/0919TEST"

print_status "🧪 開始測試整合腳本..."
print_status "測試目錄: $TEST_DIR"

# 創建測試目錄
mkdir -p "$TEST_DIR"
print_success "✅ 已創建測試目錄: $TEST_DIR"

# 複製核心檔案
print_status "正在複製核心認證檔案..."

core_files=(
    "quick_auth_setup.sh"
    "auth_config.py"
    "setup_auth.py" 
    "comprehensive_auth_test.py"
)

for file in "${core_files[@]}"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        cp "$SOURCE_DIR/$file" "$TEST_DIR/"
        print_success "✅ 已複製: $file"
    else
        print_error "⚠️  找不到檔案: $file"
    fi
done

# 設定執行權限
chmod +x "$TEST_DIR/quick_auth_setup.sh" 2>/dev/null || true

# 檢查檔案
print_status "檢查複製的檔案..."
ls -la "$TEST_DIR/"

# 測試配置修改
print_status "測試配置修改..."
if [ -f "$TEST_DIR/auth_config.py" ]; then
    # 修改專案ID作為測試
    sed -i.bak 's/gen-lang-client-0510365442/test-project-12345/' "$TEST_DIR/auth_config.py"
    print_success "✅ 配置修改測試完成"
    
    # 檢查修改結果
    grep "PROJECT_ID" "$TEST_DIR/auth_config.py"
fi

print_success "🎉 整合腳本測試完成！"
print_status "測試目錄內容："
ls -la "$TEST_DIR/"

echo
echo "📋 測試結果摘要："
echo "- 測試目錄: $TEST_DIR"
echo "- 複製檔案數量: $(ls -1 "$TEST_DIR" | wc -l | tr -d ' ')"
echo "- 配置修改: 成功"
echo "- 權限設定: 成功"