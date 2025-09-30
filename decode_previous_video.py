#!/usr/bin/env python3
"""
解碼之前生成的 Base64 影片資料並儲存為 MP4 檔案
"""

import base64
import os
import subprocess
import json
import time
import requests
from datetime import datetime


class Base64VideoDecoder:
    """Base64 影片解碼器"""
    
    def __init__(self):
        self.project_id = "gen-lang-client-0510365442"
        self.location = "us-central1"
        self.output_dir = "/Users/jianjunneng/0908test/veo_videos"
        
        # 確保輸出目錄存在
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 影片儲存目錄: {self.output_dir}")
    
    def get_access_token(self) -> str:
        """獲取存取權杖"""
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    def get_last_operation_result(self) -> dict:
        """重新獲取之前操作的結果"""
        
        print("🔍 正在重新獲取之前的影片生成結果...")
        
        # 我們需要重新運行一個快速測試來獲取結果
        # 使用相同的參數
        url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-fast-generate-001:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "instances": [{
                "prompt": "美女在星巴克喝拿鐵咖啡"
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
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API 請求失敗: {response.status_code} - {response.text}")
        
        result = response.json()
        operation_name = result.get("name")
        
        print(f"✅ 請求已提交，等待生成完成...")
        
        # 等待完成
        return self.wait_for_completion(operation_name)
    
    def wait_for_completion(self, operation_name: str, max_wait: int = 300) -> dict:
        """等待操作完成"""
        
        model_id = "veo-3.0-fast-generate-001"
        poll_url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:fetchPredictOperation"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        poll_payload = {"operationName": operation_name}
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < max_wait:
            check_count += 1
            elapsed = int(time.time() - start_time)
            
            response = requests.post(poll_url, headers=headers, json=poll_payload)
            
            if response.status_code == 200:
                status = response.json()
                
                if status.get("done", False):
                    print(f"\n🎉 影片生成完成！(總時間: {elapsed} 秒)")
                    return status
                else:
                    print(f"   檢查 {check_count}: 處理中... (已等待 {elapsed} 秒)")
            
            time.sleep(15)
        
        raise Exception(f"等待超時 ({max_wait} 秒)")
    
    def save_base64_video(self, base64_data: str, filename_prefix: str = "veo_rose") -> str:
        """將 Base64 資料解碼並儲存為 MP4 檔案"""
        
        print("🔄 正在解碼 Base64 影片資料...")
        
        try:
            # 解碼 Base64 資料
            video_bytes = base64.b64decode(base64_data)
            
            # 生成檔名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            
            # 寫入檔案
            with open(filepath, "wb") as f:
                f.write(video_bytes)
            
            file_size = len(video_bytes) / (1024 * 1024)  # MB
            
            print(f"\n🎥 影片已成功儲存！")
            print(f"📁 檔案位置: {filepath}")
            print(f"📏 檔案大小: {file_size:.2f} MB")
            print(f"🎬 格式: video/mp4")
            
            return filepath
            
        except Exception as e:
            print(f"❌ 解碼失敗: {str(e)}")
            raise
    
    def open_video(self, filepath: str):
        """在預設播放器中開啟影片"""
        try:
            subprocess.run(["open", filepath], check=True)
            print(f"🚀 已在預設播放器中開啟影片")
        except Exception as e:
            print(f"⚠️ 無法自動開啟影片: {e}")
            print(f"📺 請手動開啟檔案: {filepath}")
    
    def open_finder(self):
        """在 Finder 中開啟儲存目錄"""
        try:
            subprocess.run(["open", self.output_dir], check=True)
            print(f"📂 已在 Finder 中開啟目錄: {self.output_dir}")
        except Exception as e:
            print(f"⚠️ 無法開啟 Finder: {e}")
    
    def process_previous_video(self):
        """處理之前生成的影片"""
        
        print("🎬 Veo 影片解碼與儲存工具")
        print("=" * 50)
        print("🌹 處理之前生成的玫瑰花影片")
        print()
        
        try:
            # 重新獲取之前的操作結果
            result = self.get_last_operation_result()
            
            # 檢查回應
            if "response" not in result:
                print("❌ 沒有找到回應資料")
                return
            
            response_data = result["response"]
            videos = response_data.get("videos", [])
            
            if not videos:
                print("❌ 沒有找到影片資料")
                return
            
            video = videos[0]  # 取第一個影片
            
            if "bytesBase64Encoded" not in video:
                print("❌ 影片不是 Base64 格式")
                return
            
            # 顯示影片資訊
            base64_data = video["bytesBase64Encoded"]
            data_size = len(base64_data)
            estimated_mb = (data_size * 3 / 4) / (1024 * 1024)  # Base64 解碼後大約是原大小的 3/4
            
            print(f"📊 找到影片資料:")
            print(f"   Base64 資料大小: {data_size:,} 字符")
            print(f"   預估影片大小: {estimated_mb:.2f} MB")
            print(f"   格式: {video.get('mimeType', 'video/mp4')}")
            print()
            
            # 儲存影片
            filepath = self.save_base64_video(base64_data)
            
            # 詢問是否開啟
            print("\n選擇操作:")
            print("1. 在影片播放器中開啟")
            print("2. 在 Finder 中顯示檔案")
            print("3. 兩者都要")
            print("4. 不開啟")
            
            choice = input("請選擇 (1-4): ").strip()
            
            if choice == "1":
                self.open_video(filepath)
            elif choice == "2":
                self.open_finder()
            elif choice == "3":
                self.open_video(filepath)
                self.open_finder()
            
            print(f"\n✅ 完成！")
            print(f"📁 影片已儲存到: {filepath}")
            print(f"📂 資料夾位置: {self.output_dir}")
            
        except KeyboardInterrupt:
            print("\n❌ 操作已取消")
        except Exception as e:
            print(f"❌ 發生錯誤: {str(e)}")


if __name__ == "__main__":
    decoder = Base64VideoDecoder()
    decoder.process_previous_video()