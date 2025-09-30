#!/bin/bash

# 🎬 Veo AI 影片生成 - 一鍵啟動腳本
# 適用於完整獨立的 0919TEST 環境

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII 藝術標題
echo -e "${PURPLE}"
cat << "EOF"
╔══════════════════════════════════════════════════╗
║                                                  ║
║           🎬 Veo AI 影片生成環境                ║
║              完整測試套件 v1.0                   ║
║                                                  ║
║              創建日期: 2025/09/19                ║
╚══════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_step() {
    echo -e "${CYAN}[步驟]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[錯誤]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[資訊]${NC} $1"
}

# 檢查當前目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="$(basename "$SCRIPT_DIR")"

if [ "$PROJECT_NAME" != "0919TEST" ]; then
    print_warning "當前目錄: $PROJECT_NAME"
    print_info "建議在 0919TEST 資料夾中執行此腳本"
fi

print_info "工作目錄: $SCRIPT_DIR"
echo

# 主選單
show_menu() {
    echo -e "${BLUE}請選擇要執行的操作：${NC}"
    echo
    echo "  ${GREEN}1.${NC} 🔧 認證設定 (首次使用必須)"
    echo "  ${GREEN}2.${NC} 🎬 生成影片 (推薦)"
    echo "  ${GREEN}3.${NC} 🧪 執行測試"
    echo "  ${GREEN}4.${NC} 📁 檢視生成的影片"
    echo "  ${GREEN}5.${NC} ⚙️ 進階選項"
    echo "  ${GREEN}6.${NC} 📚 查看說明文件"
    echo "  ${GREEN}0.${NC} 🚪 退出"
    echo
    echo -n "請輸入選項 (0-6): "
}

# 認證設定
setup_auth() {
    print_step "執行認證設定..."
    echo
    
    if [ -f "./quick_auth_setup.sh" ]; then
        chmod +x ./quick_auth_setup.sh
        ./quick_auth_setup.sh
    else
        print_error "找不到認證設定腳本"
        return 1
    fi
    
    echo
    print_success "認證設定完成"
}

# 生成影片
generate_video() {
    print_step "準備生成影片..."
    
    # 檢查虛擬環境
    if [ -d "./venv" ]; then
        print_info "啟動虛擬環境..."
        source ./venv/bin/activate
    else
        print_warning "未找到虛擬環境，使用系統 Python"
    fi
    
    # 檢查主要腳本
    if [ -f "./decode_previous_video.py" ]; then
        print_info "執行 decode_previous_video.py..."
        echo
        python decode_previous_video.py
        
        if [ $? -eq 0 ]; then
            echo
            print_success "影片生成成功！"
            
            # 檢查是否有新生成的影片
            if [ -d "./veo_videos" ]; then
                LATEST_VIDEO=$(ls -t ./veo_videos/*.mp4 2>/dev/null | head -1)
                if [ -n "$LATEST_VIDEO" ]; then
                    print_info "最新影片: $(basename "$LATEST_VIDEO")"
                    echo
                    echo -n "是否要開啟影片檔案夾？(y/n): "
                    read -n 1 open_choice
                    echo
                    if [[ $open_choice =~ ^[Yy]$ ]]; then
                        open ./veo_videos/
                    fi
                fi
            fi
        else
            print_error "影片生成失敗"
        fi
    else
        print_error "找不到主要生成腳本"
        return 1
    fi
}

# 執行測試
run_tests() {
    print_step "執行測試套件..."
    
    if [ -d "./venv" ]; then
        source ./venv/bin/activate
    fi
    
    echo
    echo "選擇測試類型："
    echo "  1. 認證測試"
    echo "  2. API 結構測試"
    echo "  3. 完整功能測試"
    echo "  4. Veo 3.0 專門測試"
    echo
    echo -n "請選擇 (1-4): "
    read test_choice
    
    case $test_choice in
        1)
            print_info "執行認證測試..."
            python comprehensive_auth_test.py
            ;;
        2)
            print_info "執行 API 結構測試..."
            python structure_test.py
            ;;
        3)
            print_info "執行完整功能測試..."
            python comprehensive_test.py
            ;;
        4)
            if [ -d "./veo3_test_env" ]; then
                print_info "執行 Veo 3.0 專門測試..."
                cd veo3_test_env
                python test_veo3.py
                cd ..
            else
                print_error "找不到 Veo 3.0 測試環境"
            fi
            ;;
        *)
            print_warning "無效選項"
            ;;
    esac
}

# 檢視影片
view_videos() {
    if [ -d "./veo_videos" ]; then
        VIDEO_COUNT=$(ls ./veo_videos/*.mp4 2>/dev/null | wc -l)
        
        if [ $VIDEO_COUNT -gt 0 ]; then
            print_success "找到 $VIDEO_COUNT 個影片檔案"
            echo
            
            # 列出所有影片
            print_info "影片列表:"
            ls -lt ./veo_videos/*.mp4 | while read line; do
                echo "  $(echo $line | awk '{print $9}') ($(echo $line | awk '{print $6, $7, $8}'))"
            done
            
            echo
            echo -n "是否要開啟影片檔案夾？(y/n): "
            read -n 1 open_choice
            echo
            if [[ $open_choice =~ ^[Yy]$ ]]; then
                open ./veo_videos/
            fi
        else
            print_warning "veo_videos 資料夾中沒有影片檔案"
        fi
    else
        print_warning "找不到 veo_videos 資料夾"
        echo -n "是否要建立資料夾？(y/n): "
        read -n 1 create_choice
        echo
        if [[ $create_choice =~ ^[Yy]$ ]]; then
            mkdir -p ./veo_videos
            print_success "已建立 veo_videos 資料夾"
        fi
    fi
}

# 進階選項
advanced_options() {
    echo
    echo "進階選項："
    echo "  1. 檢查環境狀態"
    echo "  2. 重新建立虛擬環境"
    echo "  3. 編輯配置檔案"
    echo "  4. 清理暫存檔案"
    echo "  5. 匯出設定"
    echo
    echo -n "請選擇 (1-5): "
    read adv_choice
    
    case $adv_choice in
        1)
            print_info "檢查環境狀態..."
            echo
            echo "Python 版本:"
            python --version
            echo
            echo "gcloud 狀態:"
            gcloud auth list 2>/dev/null || echo "未安裝 gcloud CLI"
            echo
            echo "專案設定:"
            gcloud config get-value project 2>/dev/null || echo "未設定專案"
            ;;
        2)
            print_info "重新建立虛擬環境..."
            rm -rf ./venv
            python -m venv venv
            source ./venv/bin/activate
            if [ -f "requirements.txt" ]; then
                pip install -r requirements.txt
            else
                pip install requests google-cloud-aiplatform
            fi
            print_success "虛擬環境重新建立完成"
            ;;
        3)
            if [ -f "./auth_config.py" ]; then
                print_info "開啟配置檔案編輯..."
                ${EDITOR:-nano} ./auth_config.py
            else
                print_warning "找不到配置檔案"
            fi
            ;;
        4)
            print_info "清理暫存檔案..."
            rm -rf __pycache__/ .pytest_cache/ *.pyc
            find . -name "*.log" -delete
            print_success "清理完成"
            ;;
        5)
            print_info "匯出目前設定..."
            {
                echo "# Veo AI 環境設定匯出"
                echo "# 匯出時間: $(date)"
                echo
                echo "專案ID: $(gcloud config get-value project 2>/dev/null || echo 'N/A')"
                echo "認證帳戶: $(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null || echo 'N/A')"
                echo "Python 版本: $(python --version 2>&1)"
                echo "工作目錄: $SCRIPT_DIR"
            } > veo_config_export.txt
            print_success "設定已匯出至 veo_config_export.txt"
            ;;
        *)
            print_warning "無效選項"
            ;;
    esac
}

# 查看說明文件
view_docs() {
    echo
    echo "說明文件："
    echo "  1. 專案說明 (PROJECT_README.md)"
    echo "  2. 認證設定指南 (AUTH_SETUP_GUIDE.md)"
    echo "  3. 自動化摘要 (AUTOMATION_SUMMARY.md)"
    echo "  4. 原始說明 (README.md)"
    echo
    echo -n "請選擇要查看的文件 (1-4): "
    read doc_choice
    
    case $doc_choice in
        1) 
            if [ -f "./PROJECT_README.md" ]; then
                cat ./PROJECT_README.md | head -50
                echo
                echo "... (檔案內容較長，使用 'cat PROJECT_README.md' 查看完整內容)"
            else
                print_warning "找不到 PROJECT_README.md"
            fi
            ;;
        2)
            if [ -f "./AUTH_SETUP_GUIDE.md" ]; then
                cat ./AUTH_SETUP_GUIDE.md | head -50
                echo
                echo "... (檔案內容較長，使用 'cat AUTH_SETUP_GUIDE.md' 查看完整內容)"
            else
                print_warning "找不到 AUTH_SETUP_GUIDE.md"
            fi
            ;;
        3)
            if [ -f "./AUTOMATION_SUMMARY.md" ]; then
                cat ./AUTOMATION_SUMMARY.md | head -50
                echo
                echo "... (檔案內容較長，使用 'cat AUTOMATION_SUMMARY.md' 查看完整內容)"
            else
                print_warning "找不到 AUTOMATION_SUMMARY.md"
            fi
            ;;
        4)
            if [ -f "./README.md" ]; then
                cat ./README.md
            else
                print_warning "找不到 README.md"
            fi
            ;;
        *)
            print_warning "無效選項"
            ;;
    esac
}

# 主程序循環
main() {
    while true; do
        echo
        show_menu
        read choice
        echo
        
        case $choice in
            1)
                setup_auth
                ;;
            2)
                generate_video
                ;;
            3)
                run_tests
                ;;
            4)
                view_videos
                ;;
            5)
                advanced_options
                ;;
            6)
                view_docs
                ;;
            0)
                print_info "謝謝使用 Veo AI 影片生成環境！"
                exit 0
                ;;
            *)
                print_warning "無效選項，請選擇 0-6"
                ;;
        esac
        
        echo
        echo -n "按 Enter 鍵繼續..."
        read
    done
}

# 執行主程序
main