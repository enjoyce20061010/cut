# Google Cloud 認證設定檔
# 在執行認證腳本前，請先編輯此檔案

# ====================
# 必要設定項目
# ====================

# Google Cloud 專案 ID（必須）
PROJECT_ID = "gen-lang-client-0510365442"

# 預設地區（建議）
DEFAULT_REGION = "us-central1"

# ====================
# 可選設定項目
# ====================

# 是否自動安裝 gcloud CLI (僅 macOS + Homebrew)
AUTO_INSTALL_GCLOUD = True

# 是否自動啟用必要的 API
AUTO_ENABLE_APIS = True

# 需要啟用的 Google Cloud API 列表
REQUIRED_APIS = [
    "aiplatform.googleapis.com",     # Vertex AI API
    "compute.googleapis.com"         # Compute Engine API
]

# ====================
# 進階設定（可選）
# ====================

# 服務帳戶金鑰檔案路徑（如果使用服務帳戶）
# SERVICE_ACCOUNT_KEY_PATH = "/path/to/service-account-key.json"

# 自訂認證範圍
AUTH_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform"
]

# 是否在設定完成後執行測試
RUN_TESTS_AFTER_SETUP = True

# ====================
# 輸出設定
# ====================

# 是否顯示詳細日誌
VERBOSE_LOGGING = True

# 是否儲存認證日誌
SAVE_AUTH_LOG = True
AUTH_LOG_FILE = "auth_setup.log"

# ====================
# 安全設定
# ====================

# 認證權杖有效期檢查（小時）
TOKEN_VALIDITY_HOURS = 1

# 是否在腳本結束後清理暫存檔案
CLEANUP_TEMP_FILES = True