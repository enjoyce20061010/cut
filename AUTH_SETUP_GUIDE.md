# Google Cloud CLI 認證自動化指南

## 📋 概述

此套件提供了三種方式來自動化 Google Cloud CLI 認證設定：

1. **Python 完整版** (`setup_auth.py`) - 功能最完整
2. **Shell 快速版** (`quick_auth_setup.sh`) - 最簡單快速
3. **配置檔案** (`auth_config.py`) - 自訂設定

## 🚀 快速開始

### 方式一：使用 Shell 腳本（推薦）

```bash
# 直接執行
./quick_auth_setup.sh

# 或指定專案 ID
PROJECT_ID="your-project-id" ./quick_auth_setup.sh
```

### 方式二：使用 Python 腳本

```bash
# 使用預設專案 ID
python setup_auth.py

# 指定專案 ID
python setup_auth.py your-project-id
```

## 🔧 認證流程說明

### 完全自動化的部分 ✅
- ✅ 檢查 Google Cloud CLI 安裝狀態
- ✅ 自動安裝 gcloud CLI（macOS + Homebrew）
- ✅ 檢查目前認證狀態
- ✅ 設定專案 ID
- ✅ 啟用必要的 Google Cloud API
- ✅ 測試認證和 API 連線
- ✅ 提供詳細的錯誤診斷

### 需要手動操作的部分 ⚠️
- ⚠️ **初次 Google 帳戶登入**（需要瀏覽器互動）
- ⚠️ Linux 系統的 gcloud CLI 安裝
- ⚠️ 服務帳戶金鑰檔案設定（可選）

## 📝 需要準備的資料

### 必要資料
1. **Google Cloud 專案 ID**
   - 預設：`gen-lang-client-0510365442`
   - 可在腳本中修改或通過參數指定

2. **Google 帳戶**
   - 需要有專案的存取權限
   - 建議使用專案擁有者帳戶

### 可選資料
1. **地區設定**
   - 預設：`us-central1`
   - 可在配置檔案中修改

2. **服務帳戶金鑰**（進階用戶）
   - 完全自動化的選項
   - 不需要瀏覽器登入

## 🔐 認證方式比較

| 方式 | 自動化程度 | 安全性 | 適用場景 |
|------|------------|--------|----------|
| 使用者帳戶 | 部分自動 | 高 | 開發測試 |
| 服務帳戶 | 完全自動 | 中 | 生產環境 |

## 📋 詳細步驟說明

### 1. 環境檢查
```bash
# 檢查作業系統
uname -s

# 檢查是否已安裝 gcloud
which gcloud
gcloud --version
```

### 2. 安裝 Google Cloud CLI

#### macOS (自動)
```bash
# 檢查 Homebrew
brew --version

# 自動安裝
brew install --cask google-cloud-sdk
```

#### Linux (手動)
```bash
# Ubuntu/Debian
sudo apt-get install google-cloud-cli

# CentOS/RHEL
sudo yum install google-cloud-cli
```

#### Windows (手動)
下載安裝程式：https://cloud.google.com/sdk/docs/install-sdk

### 3. 認證流程
```bash
# 初次登入（需要瀏覽器）
gcloud auth login

# 檢查認證狀態
gcloud auth list

# 設定專案
gcloud config set project PROJECT_ID

# 設定地區
gcloud config set compute/region us-central1
```

### 4. API 啟用
```bash
# 啟用 Vertex AI API
gcloud services enable aiplatform.googleapis.com

# 啟用 Compute Engine API
gcloud services enable compute.googleapis.com
```

### 5. 測試認證
```bash
# 獲取存取權杖
gcloud auth print-access-token

# 測試 API 呼叫
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1
```

## 🤖 服務帳戶設定（進階）

### 建立服務帳戶
1. 前往 [Google Cloud Console](https://console.cloud.google.com)
2. 導航至 **IAM & Admin > Service Accounts**
3. 點擊 **Create Service Account**
4. 設定名稱和描述
5. 分配角色：**Vertex AI User** 和 **Compute Admin**
6. 下載 JSON 金鑰檔案

### 使用服務帳戶
```bash
# 方式一：環境變數
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# 方式二：gcloud 認證
gcloud auth activate-service-account --key-file="/path/to/key.json"

# 方式三：Python 代碼
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/key.json'
```

## 🛠️ 自訂配置

編輯 `auth_config.py` 檔案來自訂設定：

```python
# 修改專案 ID
PROJECT_ID = "your-project-id"

# 修改預設地區
DEFAULT_REGION = "asia-east1"

# 啟用自動安裝
AUTO_INSTALL_GCLOUD = True

# 自訂 API 列表
REQUIRED_APIS = [
    "aiplatform.googleapis.com",
    "compute.googleapis.com",
    "storage.googleapis.com"
]
```

## 🔍 故障排除

### 常見問題

#### 1. 找不到 gcloud 命令
```bash
# macOS - 重新載入 PATH
export PATH="/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/bin:$PATH"

# 或重新啟動終端
```

#### 2. 認證失敗
```bash
# 清除舊認證
gcloud auth revoke --all

# 重新認證
gcloud auth login
```

#### 3. 專案權限不足
- 確認 Google 帳戶有專案存取權限
- 檢查是否為專案擁有者或編輯者

#### 4. API 啟用失敗
```bash
# 手動啟用
gcloud services enable aiplatform.googleapis.com --project=PROJECT_ID

# 檢查計費設定
gcloud billing accounts list
```

## ⚡ 快速測試

設定完成後，執行以下命令測試：

```bash
# 測試認證
gcloud auth list

# 測試專案設定
gcloud config get-value project

# 測試 API 存取
python decode_previous_video.py
```

## 📞 支援資源

- [Google Cloud CLI 官方文件](https://cloud.google.com/sdk/docs)
- [Vertex AI 認證指南](https://cloud.google.com/vertex-ai/docs/authentication)
- [服務帳戶最佳實踐](https://cloud.google.com/iam/docs/service-accounts)

---

## 🎯 使用摘要

**最簡單的方式：**
1. 執行 `./quick_auth_setup.sh`
2. 在瀏覽器中登入 Google 帳戶
3. 等待自動設定完成
4. 執行 `python decode_previous_video.py` 測試

**需要輸入的資料：**
- Google Cloud 專案 ID（預設已提供）
- Google 帳戶登入（瀏覽器互動）
- 確認安裝選項（y/n）