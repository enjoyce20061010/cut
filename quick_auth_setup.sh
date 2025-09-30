#!/bin/bash

# Google Cloud CLI 快速認證腳本
# 適用於 macOS/Linux 系統

set -e  # 遇到錯誤立即退出

echo "🚀 Google Cloud CLI 快速設定腳本"
echo "=================================="

# 設定變數
PROJECT_ID="gen-lang-client-0510365442"
REGION="us-central1"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查作業系統
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

print_status "偵測到作業系統: $MACHINE"

# 步驟 1: 檢查 gcloud 是否已安裝
check_gcloud() {
    if command -v gcloud >/dev/null 2>&1; then
        print_success "Google Cloud CLI 已安裝"
        gcloud --version | head -1
        return 0
    else
        print_warning "Google Cloud CLI 未安裝"
        return 1
    fi
}

# 步驟 2: 安裝 gcloud CLI
install_gcloud() {
    print_status "開始安裝 Google Cloud CLI..."
    
    case $MACHINE in
        Mac)
            if command -v brew >/dev/null 2>&1; then
                print_status "使用 Homebrew 安裝..."
                brew install --cask google-cloud-sdk
                print_success "安裝完成"
            else
                print_error "未找到 Homebrew，請手動安裝："
                print_status "1. 安裝 Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                print_status "2. 安裝 gcloud: brew install --cask google-cloud-sdk"
                exit 1
            fi
            ;;
        Linux)
            print_status "Linux 安裝指引："
            print_status "Ubuntu/Debian: sudo apt-get install google-cloud-cli"
            print_status "或訪問: https://cloud.google.com/sdk/docs/install-sdk"
            read -p "請手動安裝後按 Enter 鍵繼續..."
            ;;
        *)
            print_error "不支援的作業系統: $MACHINE"
            exit 1
            ;;
    esac
}

# 步驟 3: 檢查認證狀態
check_auth() {
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
        print_success "已認證帳戶: $ACTIVE_ACCOUNT"
        return 0
    else
        print_warning "尚未認證 Google 帳戶"
        return 1
    fi
}

# 步驟 4: 執行認證
perform_auth() {
    print_status "開始 Google Cloud 認證..."
    print_status "這將開啟瀏覽器，請使用您的 Google 帳戶登入"
    
    read -p "按 Enter 鍵繼續..."
    
    if gcloud auth login; then
        print_success "認證成功"
        return 0
    else
        print_error "認證失敗"
        return 1
    fi
}

# 步驟 5: 設定專案
set_project() {
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
    
    if [ "$CURRENT_PROJECT" = "$PROJECT_ID" ]; then
        print_success "專案已設定: $PROJECT_ID"
        return 0
    fi
    
    print_status "設定專案為: $PROJECT_ID"
    
    if gcloud config set project "$PROJECT_ID"; then
        print_success "專案設定完成"
        return 0
    else
        print_error "專案設定失敗"
        return 1
    fi
}

# 步驟 6: 啟用 API
enable_apis() {
    print_status "啟用必要的 Google Cloud API..."
    
    APIS=(
        "aiplatform.googleapis.com"
        "compute.googleapis.com"
    )
    
    for api in "${APIS[@]}"; do
        print_status "啟用 $api..."
        if gcloud services enable "$api" 2>/dev/null; then
            print_success "$api 已啟用"
        else
            print_warning "$api 啟用失敗（可能已啟用或權限不足）"
        fi
    done
}

# 步驟 7: 測試認證
test_auth() {
    print_status "測試認證..."
    
    if TOKEN=$(gcloud auth print-access-token 2>/dev/null); then
        if [ ${#TOKEN} -gt 50 ]; then
            print_success "存取權杖獲取成功"
            
            # 測試 API 呼叫
            print_status "測試 Vertex AI API 連線..."
            API_URL="https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION"
            
            if curl -s -o /dev/null -w "%{http_code}" \
                -H "Authorization: Bearer $TOKEN" \
                "$API_URL" | grep -q "^[24]"; then
                print_success "API 連線測試成功"
                return 0
            else
                print_warning "API 連線測試失敗（可能是權限問題）"
                return 1
            fi
        else
            print_error "存取權杖無效"
            return 1
        fi
    else
        print_error "無法獲取存取權杖"
        return 1
    fi
}

# 主要執行流程
main() {
    echo
    print_status "目標專案: $PROJECT_ID"
    print_status "目標地區: $REGION"
    echo
    
    # 檢查並安裝 gcloud
    if ! check_gcloud; then
        echo
        read -p "是否要自動安裝 Google Cloud CLI? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_gcloud
            
            # 重新載入環境
            if [ $MACHINE = "Mac" ]; then
                export PATH="/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/bin:$PATH"
            fi
            
            if ! check_gcloud; then
                print_error "安裝後仍無法找到 gcloud，請重新啟動終端"
                exit 1
            fi
        else
            print_status "請手動安裝 Google Cloud CLI 後重新執行此腳本"
            exit 0
        fi
    fi
    
    echo
    
    # 檢查並執行認證
    if ! check_auth; then
        echo
        if ! perform_auth; then
            print_error "認證失敗，腳本終止"
            exit 1
        fi
    fi
    
    echo
    
    # 設定專案
    if ! set_project; then
        print_error "專案設定失敗，腳本終止"
        exit 1
    fi
    
    echo
    
    # 啟用 API
    enable_apis
    
    echo
    
    # 測試認證
    if test_auth; then
        echo
        print_success "🎉 所有設定完成！"
        print_success "現在您可以使用 Veo API 了"
        echo
        print_status "快速測試命令："
        print_status "python decode_previous_video.py"
        echo
    else
        echo
        print_warning "設定完成，但認證測試失敗"
        print_status "您仍然可以嘗試使用 Veo API"
        echo
    fi
}

# 執行主程序
main "$@"