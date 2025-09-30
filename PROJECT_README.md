# 🎬 Veo AI 影片生成完整測試環境 (0919TEST)

> 最優先請先閱讀並執行：[`TOP_START.md`](./TOP_START.md) — 三步完成認證、連線、與生成影片（建議所有人先看這份即可）。

## 📋 專案概述

這是一個完整的 Google Veo AI 影片生成測試環境，包含所有必要的工具、腳本和測試檔案。

**創建日期**: 2025年9月19日
**版本**: v1.0
**支援模型**: Veo 2.0, Veo 3.0 (含所有變體)

## 📁 目錄結構

```
0919TEST/
├── 🔧 認證設定工具
│   ├── quick_auth_setup.sh        # Shell 快速認證設定
│   ├── setup_auth.py              # Python 完整認證設定  
│   ├── auth_config.py             # 認證配置檔
│   └── comprehensive_auth_test.py # 認證測試腳本
│
├── 🎬 影片生成腳本
│   ├── decode_previous_video.py   # 主要影片生成腳本 (推薦)
│   ├── text_to_video.py          # 文字轉影片
│   ├── image_to_video.py         # 圖片轉影片
│   ├── comprehensive_test.py     # 綜合測試
│   └── direct_test.py            # 直接 API 測試
│
├── 🧪 測試環境
│   ├── veo3_test_env/            # Veo 3.0 測試環境
│   ├── structure_test.py         # API 結構測試
│   ├── quick_test.py            # 快速功能測試
│   └── save_video.py            # 影片儲存工具
│
├── 🎥 輸出檔案
│   └── veo_videos/              # 生成的影片檔案
│
├── 📚 說明文件
│   ├── AUTH_SETUP_GUIDE.md      # 認證設定詳細指南
│   ├── AUTOMATION_SUMMARY.md    # 自動化功能摘要
│   └── README.md               # 原始說明檔案
│
└── 🐍 Python 環境
    └── venv/                    # 虛擬環境 (已配置)
```

## 🚀 快速開始

### 1. 一鍵設定 (推薦)
```bash
cd /Users/jianjunneng/0908test/0919TEST
./quick_auth_setup.sh
```

### 2. 生成您的第一個影片
```bash
# 啟動虛擬環境
source venv/bin/activate

# 生成影片 (修改腳本中的 prompt 來自訂內容)
python decode_previous_video.py
```

### 3. 檢視生成的影片
```bash
# 生成的影片會自動儲存在 veo_videos/ 資料夾
open veo_videos/
```

## 🛠️ 詳細使用說明

### 認證設定
```bash
# 方式 1: 快速設定 (Shell)
./quick_auth_setup.sh

# 方式 2: 完整設定 (Python)
python setup_auth.py

# 方式 3: 測試現有認證
python comprehensive_auth_test.py
```

### 影片生成選項

#### 🎯 推薦使用
```bash
python decode_previous_video.py
```
**功能**: 完整的 Veo 3.0 影片生成，包含 Base64 解碼和檔案儲存

#### 🔧 其他選項
```bash
# 文字轉影片
python text_to_video.py

# 圖片轉影片  
python image_to_video.py

# 綜合測試
python comprehensive_test.py
```

### 測試和驗證
```bash
# API 結構測試 (不需認證)
python structure_test.py

# 快速功能測試
python quick_test.py

# Veo 3.0 專門測試
cd veo3_test_env
python test_veo3.py
```

## ⚙️ 配置說明

### 專案設定
- **專案 ID**: `gen-lang-client-0510365442`
- **地區**: `us-central1`
- **支援模型**: 
  - `veo-2.0-generate-001`
  - `veo-3.0-generate-001` (推薦)
  - `veo-3.0-fast-generate-001`

### 自訂配置
編輯 `auth_config.py` 來自訂：
- 專案 ID
- 預設地區  
- API 設定
- 輸出選項

## 🎬 影片生成範例

### 修改提示詞
在 `decode_previous_video.py` 中找到並修改：

```python
payload = {
    "prompt": "您的自訂提示詞",  # 在這裡修改
    "durationSeconds": 6,        # 影片長度 (2-60秒)
    "resolution": "720p",        # 解析度 (540p, 720p, 1080p)
    "generateAudio": true        # 是否生成音訊
}
```

### 輸出格式
- **檔案格式**: MP4
- **命名規則**: `veo_[描述]_YYYYMMDD_HHMMSS.mp4`
- **儲存位置**: `veo_videos/` 資料夾

## 🔍 故障排除

### 常見問題

#### 1. 認證失敗
```bash
# 重新認證
gcloud auth login
./quick_auth_setup.sh
```

#### 2. 模型存取被拒絕
- 確認 Google Cloud 專案有 Vertex AI 存取權限
- 檢查帳戶是否為專案擁有者或編輯者

#### 3. 虛擬環境問題
```bash
# 重新創建虛擬環境
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. API 請求失敗
```bash
# 檢查認證狀態
python comprehensive_auth_test.py
```

## 📊 功能特色

### ✅ 完整功能
- 🔐 **自動化認證設定** (90% 自動化)
- 🎬 **多種影片生成方式** (文字、圖片轉影片)
- 📹 **所有 Veo 模型支援** (2.0/3.0 全系列)
- 💾 **自動檔案儲存** (Base64 → MP4 轉換)
- 🧪 **完整測試套件** (認證、功能、API 測試)
- 📚 **詳細說明文件** (包含故障排除)

### 🚀 優化特色  
- ⚡ **一鍵啟動** (`./quick_auth_setup.sh`)
- 🔄 **可重複使用** (獨立環境)
- 📱 **跨平台支援** (macOS/Linux)
- 🛡️ **錯誤處理** (詳細錯誤診斷)

## 📞 支援資源

- **官方文件**: [Google Vertex AI](https://cloud.google.com/vertex-ai)
- **Veo 模型**: [Google Veo](https://deepmind.google/technologies/veo/)
- **認證指南**: 查看 `AUTH_SETUP_GUIDE.md`
- **自動化摘要**: 查看 `AUTOMATION_SUMMARY.md`

## 🎯 使用摘要

**這是一個完全獨立的 Veo AI 影片生成環境！**

1. ✅ **認證**: 執行 `./quick_auth_setup.sh`
2. ✅ **生成**: 執行 `python decode_previous_video.py`  
3. ✅ **檢視**: 生成的 MP4 檔案會自動開啟

**需要的資料**:
- Google Cloud 專案 ID (已預設)
- Google 帳戶登入 (一次性瀏覽器認證)

---
*創建於 2025年9月19日 | 完整獨立的 Veo AI 測試環境*