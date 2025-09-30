import google.auth
import requests
import json
import time

def test_veo3_video_generation():
    try:
        # 取得 Google Cloud 預設憑證
        credentials, project = google.auth.default()
        
        # 刷新憑證以取得 access token
        credentials.refresh(google.auth.transport.requests.Request())
        token = credentials.token
        
        print(f"專案 ID: {project}")
        print(f"Token 前 20 字元: {token[:20]}...")
        
        # Veo 3 Fast 影片生成 API 端點
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/veo-3.0-fast-generate-001:predictLongRunning"
        
        # 請求內容
        body = {
            "instances": [{"prompt": "航拍视角，未来城市夜景，赛博朋克风格，8 s"}],
            "parameters": {"durationSeconds": 8, "sampleCount": 1}
        }
        
        print("正在發送影片生成請求...")
        
        # 發送請求
        r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body)
        
        if not r.ok:
            print(f"請求失敗: {r.status_code}")
            print(f"錯誤詳情: {r.text}")
            return
            
        operation = r.json()['name']
        print(f"操作 ID: {operation}")
        
        # 轮询直到完成
        print("正在生成影片，請稍候...")
        while True:
            op_response = requests.get(
                f"https://us-central1-aiplatform.googleapis.com/v1/{operation}", 
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if not op_response.ok:
                print(f"輪詢失敗: {op_response.status_code}")
                print(f"錯誤詳情: {op_response.text}")
                return
                
            op = op_response.json()
            
            if op.get("done"):
                break
                
            print(".", end="", flush=True)
            time.sleep(5)
        
        print("\n影片生成完成！")
        
        if 'response' in op and 'storageUri' in op['response']:
            print(f"視頻已保存至: {op['response']['storageUri']}")
        else:
            print("操作完成，但未找到儲存位置")
            print(f"完整回應: {json.dumps(op, indent=2, ensure_ascii=False)}")
            
    except google.auth.exceptions.DefaultCredentialsError:
        print("❌ 找不到 Google Cloud 憑證")
        print("請執行以下步驟設定憑證：")
        print("1. 安裝 Google Cloud CLI: https://cloud.google.com/sdk/docs/install")
        print("2. 執行: gcloud auth application-default login")
        print("3. 或設定服務帳號 JSON 金鑰檔案路徑到環境變數 GOOGLE_APPLICATION_CREDENTIALS")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    test_veo3_video_generation()