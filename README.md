# Veo API 官方測試套件

基於 Google Cloud Vertex AI 官方文檔實現的 Veo 影片生成 API 測試工具。

## 📋 支援的模型

| 模型 ID | 名稱 | 狀態 | 音訊支援 | 影片長度 | 特殊功能 |
|---------|------|------|----------|----------|----------|
| `veo-2.0-generate-001` | Veo 2.0 GA版本 | ✅ 穩定 | ❌ | 5-8秒 | - |
| `veo-2.0-generate-exp` | Veo 2.0 實驗版本 | 🧪 實驗 | ❌ | 5-8秒 | 參考圖片 |
| `veo-3.0-generate-001` | Veo 3.0 標準版本 | ✅ 穩定 | ✅ | 4,6,8秒 | 高解析度 |
| `veo-3.0-fast-generate-001` | Veo 3.0 快速版本 | ✅ 穩定 | ✅ | 4,6,8秒 | 快速生成 |
| `veo-3.0-generate-preview` | Veo 3.0 預覽版本 | 🧪 預覽 | ✅ | 4,6,8秒 | 最新功能 |
| `veo-3.0-fast-generate-preview` | Veo 3.0 快速預覽版本 | 🧪 預覽 | ✅ | 4,6,8秒 | 快速+最新 |

## 🚀 快速開始

### 1. 環境設定

```bash
# 進入測試目錄
cd /Users/jianjunneng/0908test/veo_official_test

# 啟動虛擬環境
source venv/bin/activate

# 確認套件已安裝
pip list | grep google-cloud-aiplatform
```

### 2. Google Cloud 認證

```bash
# 安裝 Google Cloud CLI (如果尚未安裝)
# https://cloud.google.com/sdk/docs/install

# 登入 Google Cloud
gcloud auth login

# 設定專案 (可選)
gcloud config set project YOUR_PROJECT_ID

# 確認認證狀態
gcloud auth list
```

### 3. 設定專案 ID

在所有 Python 腳本中，將 `PROJECT_ID` 變數修改為您的實際 Google Cloud 專案 ID：

```python
PROJECT_ID = "your-actual-project-id"  # 修改這裡
```

## 📁 腳本說明

### `text_to_video.py` - 文字轉影片
基本的文字轉影片功能測試。

```bash
python text_to_video.py
```

**功能特點：**
- 支援所有 Veo 模型
- 多種測試提示詞
- 自動長時間操作輪詢
- 結果顯示和錯誤處理

### `image_to_video.py` - 圖片轉影片
圖片轉影片功能測試（需要 Pillow 套件）。

```bash
# 安裝額外依賴
pip install Pillow

python image_to_video.py
```

**功能特點：**
- 自動生成測試圖片
- Base64 圖片編碼
- 支援 JPEG 和 PNG 格式
- 參考圖片功能（veo-2.0-generate-exp）

### `comprehensive_test.py` - 綜合測試
完整的測試套件，支援所有功能。

```bash
python comprehensive_test.py
```

**功能特點：**
- 所有模型支援檢測
- 互動式測試選擇
- 詳細進度顯示
- 全面的錯誤處理

## 🧪 使用範例

### 基本文字轉影片

```python
from text_to_video import VeoAPIClient

client = VeoAPIClient("your-project-id")

result = client.generate_video_from_text(
    prompt="一隻可愛的小貓在花園裡玩耍",
    model_id="veo-3.0-generate-001",
    duration_seconds=8,
    aspect_ratio="16:9"
)

# 等待完成
final_result = client.wait_for_completion(
    result["name"], 
    "veo-3.0-generate-001"
)
```

### 高級參數設定

```python
result = client.generate_video_from_text(
    prompt="未來城市的夜景，霓虹燈閃爍",
    model_id="veo-3.0-generate-001",
    duration_seconds=8,
    sample_count=2,  # 生成 2 個影片
    aspect_ratio="16:9",
    enhancePrompt=True,  # 使用 Gemini 增強提示
    generateAudio=True,  # 生成音訊（Veo 3.0）
    resolution="1080p",  # 高解析度（Veo 3.0）
    negativePrompt="模糊、低品質、失真",  # 負面提示
    personGeneration="allow_adult"  # 人物生成設定
)
```

## 🔧 參數說明

### 基本參數
- `prompt`: 文字提示（必填）
- `model_id`: 模型 ID（必填）
- `duration_seconds`: 影片長度，秒（必填）
- `sample_count`: 生成影片數量（1-4）
- `aspect_ratio`: 影片比例（"16:9" 或 "9:16"）

### Veo 3.0 特殊參數
- `generateAudio`: 生成音訊（true/false）
- `resolution`: 解析度（"720p" 或 "1080p"）

### 選用參數
- `enhancePrompt`: 使用 Gemini 增強提示（true/false）
- `negativePrompt`: 負面提示，避免不想要的內容
- `personGeneration`: 人物生成控制（"allow_adult"/"dont_allow"）
- `compressionQuality`: 壓縮品質（"optimized"/"lossless"）
- `seed`: 隨機種子，用於重現相同結果
- `storageUri`: Cloud Storage 儲存位置（格式: gs://bucket/path）

## 📊 輸出格式

### 成功回應
```json
{
  "name": "projects/.../operations/operation-id",
  "done": true,
  "response": {
    "@type": "type.googleapis.com/cloud.ai.large_models.vision.GenerateVideoResponse",
    "videos": [
      {
        "gcsUri": "gs://bucket/video.mp4",
        "mimeType": "video/mp4"
      }
    ],
    "raiMediaFilteredCount": 0
  }
}
```

### 安全篩選
如果內容違反政策，影片可能被篩選：
```json
{
  "raiMediaFilteredCount": 1,
  "raiMediaFilteredReasons": ["REASON_CODE"]
}
```

## ⚠️ 注意事項

### 使用限制
1. **認證要求**: 必須設定 Google Cloud CLI 認證
2. **專案權限**: 需要啟用 Vertex AI API
3. **配額限制**: 注意 API 呼叫配額和費用
4. **模型可用性**: 預覽版本模型可能不穩定

### 故障排除

**問題**: `無法獲取存取權杖`
```bash
# 解決方法
gcloud auth login
gcloud auth application-default login
```

**問題**: `API 請求失敗 [403]`
```bash
# 檢查專案權限和 API 啟用狀態
gcloud services enable aiplatform.googleapis.com
```

**問題**: `不支援的模型`
- 某些模型可能在特定地區不可用
- 預覽版本模型需要特殊權限

## 📈 效能提示

1. **選擇合適的模型**:
   - 一般用途: `veo-3.0-generate-001`
   - 快速原型: `veo-3.0-fast-generate-001`
   - 穩定性優先: `veo-2.0-generate-001`

2. **最佳化參數**:
   - 較短影片生成更快
   - 降低 sample_count 節省時間
   - 使用 "optimized" 壓縮節省儲存

3. **批次處理**:
   - 使用 `sample_count > 1` 一次生成多個變體
   - 利用 Cloud Storage 儲存減少傳輸時間

## 🔗 相關資源

- [Vertex AI Veo API 官方文檔](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/veo)
- [Google Cloud 定價](https://cloud.google.com/vertex-ai/pricing)
- [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
- [Veo Studio](https://labs.google/fx/tools/veo)

## 📝 更新日誌

- **v1.0** (2024-09-18): 初始版本，支援所有官方 Veo 模型
  - 文字轉影片功能
  - 圖片轉影片功能
  - 長時間操作輪詢
  - 綜合測試套件