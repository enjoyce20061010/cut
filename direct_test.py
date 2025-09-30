#!/usr/bin/env python3
"""
直接測試 Veo API - 使用您的專案 ID
會自動嘗試不同的地區和認證方式
"""

import subprocess
import requests
import json
import time
from typing import Optional, Dict, Any


class DirectVeoTester:
    def __init__(self):
        self.project_id = "gen-lang-client-0510365442"
        self.locations = ["us-central1", "us-east1", "us-west1", "europe-west4", "asia-southeast1"]
        self.access_token = None
        self.working_location = None
        
    def get_access_token(self) -> Optional[str]:
        """嘗試多種方式獲取存取權杖"""
        methods = [
            # 方法 1: gcloud CLI
            lambda: subprocess.run(
                ["gcloud", "auth", "print-access-token"], 
                capture_output=True, text=True, check=True
            ).stdout.strip(),
            
            # 方法 2: Google Cloud SDK
            lambda: subprocess.run(
                ["gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True, text=True, check=True
            ).stdout.strip(),
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"🔐 嘗試認證方法 {i}...")
                token = method()
                if token and len(token) > 10:
                    print(f"✅ 成功獲取存取權杖 (方法 {i})")
                    return token
            except Exception as e:
                print(f"❌ 方法 {i} 失敗: {str(e)}")
                continue
                
        return None
    
    def test_location(self, location: str) -> bool:
        """測試特定地區是否可用"""
        if not self.access_token:
            return False
            
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{location}/publishers/google/models/veo-3.0-fast-generate-001:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # 簡單的測試請求
        payload = {
            "instances": [{"prompt": "測試"}],
            "parameters": {
                "durationSeconds": 4,
                "sampleCount": 1,
                "aspectRatio": "16:9"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"   地區 {location}: HTTP {response.status_code}")
            
            if response.status_code in [200, 400]:  # 400 可能是參數問題，但地區可用
                return True
            elif response.status_code == 404:
                return False
            else:
                print(f"      回應: {response.text[:200]}")
                return response.status_code < 500
                
        except Exception as e:
            print(f"   地區 {location}: 連線錯誤 - {str(e)}")
            return False
    
    def find_working_location(self) -> Optional[str]:
        """尋找可用的地區"""
        print("🌍 測試可用地區...")
        
        for location in self.locations:
            print(f"   測試 {location}...")
            if self.test_location(location):
                print(f"✅ 找到可用地區: {location}")
                return location
                
        return None
    
    def run_simple_test(self) -> bool:
        """執行簡單的 Veo API 測試"""
        print("🚀 開始 Veo API 直接測試")
        print(f"📋 專案 ID: {self.project_id}")
        print("=" * 50)
        
        # 步驟 1: 獲取存取權杖
        self.access_token = self.get_access_token()
        if not self.access_token:
            print("\n❌ 無法獲取 Google Cloud 存取權杖")
            print("\n💡 請嘗試以下解決方案:")
            print("1. 安裝 Google Cloud CLI: https://cloud.google.com/sdk/docs/install")
            print("2. 執行認證: gcloud auth login")
            print("3. 設定專案: gcloud config set project gen-lang-client-0510365442")
            return False
        
        # 步驟 2: 尋找可用地區
        self.working_location = self.find_working_location()
        if not self.working_location:
            print("\n❌ 找不到可用的地區")
            print("可能原因:")
            print("- 專案未啟用 Vertex AI API")
            print("- 專案沒有 Veo 模型存取權限")
            print("- 網路連線問題")
            return False
        
        # 步驟 3: 執行真實測試
        print(f"\n🎬 使用地區 {self.working_location} 執行 Veo 測試...")
        
        url = f"https://{self.working_location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.working_location}/publishers/google/models/veo-3.0-fast-generate-001:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "instances": [{
                "prompt": "一朵美麗的玫瑰花在微風中輕輕搖擺，陽光透過花瓣，創造出溫暖的光影效果"
            }],
            "parameters": {
                "durationSeconds": 6,
                "sampleCount": 1,
                "aspectRatio": "16:9",
                "generateAudio": True,
                "resolution": "720p"
            }
        }
        
        print("📤 發送影片生成請求...")
        print(f"🎯 提示: {payload['instances'][0]['prompt']}")
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                operation_name = result.get("name", "")
                
                print("✅ 請求成功提交!")
                print(f"🔄 操作 ID: {operation_name.split('/')[-1] if operation_name else '未知'}")
                
                # 開始輪詢狀態
                if operation_name:
                    self.poll_operation(operation_name)
                
                return True
                
            else:
                print(f"❌ 請求失敗: HTTP {response.status_code}")
                print(f"錯誤訊息: {response.text}")
                
                # 分析錯誤
                if response.status_code == 403:
                    print("\n💡 可能的解決方案:")
                    print("- 檢查專案是否啟用 Vertex AI API")
                    print("- 確認帳戶有足夠權限")
                    print("- 檢查是否有 Veo 模型存取權限")
                elif response.status_code == 404:
                    print("\n💡 可能的問題:")
                    print("- 模型在此地區不可用")
                    print("- API 端點錯誤")
                
                return False
                
        except Exception as e:
            print(f"❌ 請求異常: {str(e)}")
            return False
    
    def poll_operation(self, operation_name: str, max_wait: int = 300):
        """輪詢操作狀態"""
        print("\n⏳ 等待影片生成完成...")
        
        # 從操作名稱提取模型 ID
        model_id = "veo-3.0-fast-generate-001"
        
        poll_url = f"https://{self.working_location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.working_location}/publishers/google/models/{model_id}:fetchPredictOperation"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        poll_payload = {
            "operationName": operation_name
        }
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < max_wait:
            check_count += 1
            elapsed = int(time.time() - start_time)
            
            try:
                response = requests.post(poll_url, headers=headers, json=poll_payload)
                
                if response.status_code == 200:
                    status = response.json()
                    
                    if status.get("done", False):
                        print("\n🎉 影片生成完成!")
                        self.display_results(status)
                        return
                    else:
                        print(f"   檢查 {check_count}: 處理中... (已等待 {elapsed} 秒)")
                        
                else:
                    print(f"   狀態檢查失敗: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   狀態檢查異常: {str(e)}")
            
            time.sleep(15)  # 每 15 秒檢查一次
        
        print(f"\n⏰ 等待超時 ({max_wait} 秒)")
        print("操作可能仍在執行中，請稍後手動檢查")
    
    def display_results(self, result: Dict[str, Any]):
        """顯示結果"""
        if "response" not in result:
            print("❌ 沒有回應資料")
            return
            
        response_data = result["response"]
        
        # 安全篩選檢查
        filtered_count = response_data.get("raiMediaFilteredCount", 0)
        if filtered_count > 0:
            print(f"⚠️ 安全篩選: {filtered_count} 個影片因內容政策被篩除")
        
        # 顯示生成的影片
        videos = response_data.get("videos", [])
        if videos:
            print(f"🎥 成功生成 {len(videos)} 個影片:")
            
            for i, video in enumerate(videos, 1):
                print(f"\n影片 {i}:")
                
                if "gcsUri" in video:
                    print(f"  📁 雲端位置: {video['gcsUri']}")
                elif "bytesBase64Encoded" in video:
                    size = len(video["bytesBase64Encoded"])
                    print(f"  💾 Base64 資料: {size:,} 字符")
                
                mime_type = video.get("mimeType", "未知")
                print(f"  🎬 格式: {mime_type}")
        else:
            print("❌ 沒有生成任何影片")


if __name__ == "__main__":
    tester = DirectVeoTester()
    success = tester.run_simple_test()
    
    if success:
        print("\n🎉 測試成功完成!")
    else:
        print("\n❌ 測試失敗，請檢查設定")