# ✅ 最優先：三步完成 Veo 連線與測試

這是本專案唯一需要先讀、先執行的文件。照這三步做，就能完成認證、確認 API 連線，並生成第一支影片 MP4。

適用環境：macOS（zsh）
工作目錄：`/Users/jianjunneng/0919TEST`

---

## 1) 一鍵認證與專案設定（必做）
```zsh
cd /Users/jianjunneng/0919TEST
chmod +x quick_auth_setup.sh
./quick_auth_setup.sh
```
成功標準：
- 出現「[SUCCESS] 已認證帳戶」
- 出現「[SUCCESS] 專案已設定: gen-lang-client-0510365442」
- 出現「[SUCCESS] API 連線測試成功」

---

## 2) 建立 Python 虛擬環境與安裝套件（一次即可）
```zsh
python3 -V
python3 -m venv venv
source venv/bin/activate
python -m ensurepip --upgrade || true
python -m pip install --upgrade pip
python -m pip install requests google-auth google-cloud-aiplatform
```
成功標準：
- `pip --version` 可執行
- `requests` / `google-cloud-aiplatform` 安裝成功

如遇 `urllib3 NotOpenSSL/LibreSSL` 警告，可先忽略；不影響測試。

---

## 3) 一鍵啟動服務器（推薦）

**最簡單的方式 - 一鍵啟動所有服務：**
```zsh
./quick_start.sh
```

成功標準：
- 顯示 "✅ 完成！"
- 顯示前端和後端 URL
- 服務器在背景運行

然後直接訪問：
- 🌐 **前端界面**: http://localhost:8080/frontend_test.html
- 📡 **後端 API**: http://localhost:8001

---

## 舊版手動啟動方式（備用）

A. 手動啟動完整影片（備用）
```zsh
source venv/bin/activate
python decode_previous_video.py
```

B. 先做快速 API 成功驗證，再選擇是否生成
```zsh
source venv/bin/activate
python comprehensive_auth_test.py
```
成功標準：
- 認證/連線/模型 3 項 PASS（功能測試若為 400 表示 payload 形狀；不影響 A 法）

---

## 常見問題（極短）
- 找不到 pip / 套件錯誤
```zsh
source venv/bin/activate
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install requests google-auth google-cloud-aiplatform
```
- 找不到 gcloud
```zsh
brew install --cask google-cloud-sdk
exec -l $SHELL
gcloud auth login
gcloud config set project gen-lang-client-0510365442
```
- 權限問題（無法執行 .sh）
```zsh
chmod +x quick_auth_setup.sh verify_environment.sh start_veo.sh
```

---

## 完成後可以做什麼？
- 修改 `decode_previous_video.py` 的提示詞與參數，生成你要的影片
- 或執行互動選單：
```zsh
./start_veo.sh
```

> 記得：只要照這份 TOP_START.md 做，3 步驟就會有結果。其他文件都可稍後再看。