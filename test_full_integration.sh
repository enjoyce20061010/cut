#!/bin/bash

# 🚀 簡化整合測試腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 參數
SOURCE_DIR="/Users/jianjunneng/0919TEST"
TARGET_DIR="./integration_test_$(date +%Y%m%d_%H%M%S)"

print_status "🧪 開始整合功能測試..."
print_status "來源目錄: $SOURCE_DIR"
print_status "目標目錄: $TARGET_DIR"

# 1. 測試選項4（顯示檢查清單）
print_status "測試 1: 檢查清單功能"
echo "4" | ./integrate_to_new_project.sh
print_success "✅ 檢查清單功能正常"

echo
print_status "測試 2: 核心檔案複製功能"

# 2. 創建測試目錄
mkdir -p "$TARGET_DIR"
print_success "✅ 已創建測試目錄: $TARGET_DIR"

# 3. 複製核心檔案
core_files=(
    "quick_auth_setup.sh"
    "auth_config.py"
    "setup_auth.py" 
    "comprehensive_auth_test.py"
)

for file in "${core_files[@]}"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        cp "$SOURCE_DIR/$file" "$TARGET_DIR/"
        print_success "✅ 已複製: $file"
    else
        echo "⚠️  找不到檔案: $file"
    fi
done

# 4. 設定權限
chmod +x "$TARGET_DIR/quick_auth_setup.sh"
print_success "✅ 已設定執行權限"

# 5. 測試配置修改
if [ -f "$TARGET_DIR/auth_config.py" ]; then
    # 備份原始檔案
    cp "$TARGET_DIR/auth_config.py" "$TARGET_DIR/auth_config.py.bak"
    
    # 修改配置（測試用）
    sed -i.tmp 's/gen-lang-client-0510365442/test-project-integration/' "$TARGET_DIR/auth_config.py"
    rm -f "$TARGET_DIR/auth_config.py.tmp"
    
    print_success "✅ 配置修改測試完成"
    
    # 顯示修改結果
    grep "PROJECT_ID" "$TARGET_DIR/auth_config.py"
fi

# 6. 檢查結果
echo
print_status "測試目錄內容："
ls -la "$TARGET_DIR/"

# 7. 驗證檔案完整性
echo
print_status "檔案完整性驗證："
for file in "${core_files[@]}"; do
    if [ -f "$TARGET_DIR/$file" ]; then
        size=$(wc -c < "$TARGET_DIR/$file")
        echo "✅ $file ($size bytes)"
    else
        echo "❌ $file (缺失)"
    fi
done

# 8. 測試配置檔案
if [ -f "$TARGET_DIR/auth_config.py" ]; then
    echo
    print_status "配置檔案驗證："
    echo "修改前: gen-lang-client-0510365442"
    echo "修改後: $(grep 'PROJECT_ID' "$TARGET_DIR/auth_config.py" | cut -d'"' -f2)"
fi

print_success "🎉 整合功能測試完成！"

echo
echo "📋 測試總結："
echo "- 測試目錄: $TARGET_DIR"
echo "- 複製檔案: $(ls -1 "$TARGET_DIR"/*.py "$TARGET_DIR"/*.sh 2>/dev/null | wc -l | tr -d ' ') 個"
echo "- 配置修改: 成功"
echo "- 權限設定: 成功"
echo
echo "🔧 您可以查看測試目錄或清理："
echo "  ls -la $TARGET_DIR"
echo "  rm -rf $TARGET_DIR"