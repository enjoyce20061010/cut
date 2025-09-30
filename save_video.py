#!/usr/bin/env python3
"""
將 Veo API 生成的 Base64 影片資料解碼並儲存為 MP4 檔案
"""

import base64
import os
import subprocess
import json
import time
import requests
from datetime import datetime


class VeoVideoSaver:
    """Veo 影片儲存工具"""
    
    def __init__(self, project_id: str = "gen-lang-client-0510365442", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
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
    
    def generate_and_save_video(
        self,
        prompt: str,
        model_id: str = "veo-3.0-fast-generate-001",
        duration: int = 6,
        filename_prefix: str = "veo_video"
    ) -> str:
        """生成影片並直接儲存到檔案"""
        
        print(f"🎬 開始生成影片...")
        print(f"📝 提示: {prompt}")
        print(f"🤖 模型: {model_id}")
        
        # API 端點
        url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "durationSeconds": duration,
                "sampleCount": 1,
                "aspectRatio": "16:9",
                "generateAudio": True,
                "resolution": "720p"
            }
        }
        
        # 發送請求
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API 請求失敗: {response.status_code} - {response.text}")
        
        result = response.json()
        operation_name = result.get("name")
        
        print(f"✅ 請求已提交，等待生成完成...")
        
        # 等待完成
        final_result = self.wait_for_completion(operation_name, model_id)
        
        # 儲存影片
        return self.save_video_from_response(final_result, filename_prefix, prompt)
    
    def wait_for_completion(self, operation_name: str, model_id: str, max_wait: int = 300) -> dict:
        """等待操作完成"""
        
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
    
    def save_video_from_response(self, result: dict, filename_prefix: str, prompt: str) -> str:
        """從 API 回應中儲存影片"""
        
        if "response" not in result:
            raise Exception("沒有回應資料")
        
        response_data = result["response"]
        videos = response_data.get("videos", [])
        
        if not videos:
            raise Exception("沒有生成任何影片")
        
        video = videos[0]  # 取第一個影片
        
        if "bytesBase64Encoded" not in video:
            raise Exception("影片不是 Base64 格式")
        
        # 解碼 Base64 資料
        base64_data = video["bytesBase64Encoded"]
        video_bytes = base64.b64decode(base64_data)
        
        # 生成檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.mp4"
        filepath = os.path.join(self.output_dir, filename)
        
        # 寫入檔案
        with open(filepath, "wb") as f:
            f.write(video_bytes)
        
        file_size = len(video_bytes) / (1024 * 1024)  # MB
        
        print(f"\n🎥 影片已儲存！")
        print(f"📁 檔案位置: {filepath}")
        print(f"📏 檔案大小: {file_size:.2f} MB")
        print(f"🎬 格式: {video.get('mimeType', 'video/mp4')}")
        
        # 建立元資料檔案
        metadata = {
            "prompt": prompt,
            "timestamp": timestamp,
            "file_size_mb": round(file_size, 2),
            "mime_type": video.get('mimeType', 'video/mp4'),
            "filtered_count": response_data.get("raiMediaFilteredCount", 0)
        }
        
        metadata_path = filepath.replace(".mp4", "_metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def open_video(self, filepath: str):
        """在預設播放器中開啟影片"""
        try:
            subprocess.run(["open", filepath], check=True)
            print(f"🚀 已在預設播放器中開啟影片")
        except Exception as e:
            print(f"⚠️ 無法自動開啟影片: {e}")
            print(f"請手動開啟: {filepath}")
    
    def list_saved_videos(self):
        """列出已儲存的影片"""
        print(f"\n📋 已儲存的影片 (位於 {self.output_dir}):")
        print("-" * 60)
        
        video_files = [f for f in os.listdir(self.output_dir) if f.endswith('.mp4')]
        
        if not video_files:
            print("   目前沒有已儲存的影片")
            return
        
        for i, filename in enumerate(sorted(video_files), 1):
            filepath = os.path.join(self.output_dir, filename)
            file_size = os.path.getsize(filepath) / (1024 * 1024)
            
            # 讀取元資料
            metadata_path = filepath.replace(".mp4", "_metadata.json")
            metadata = {}
            if os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            
            print(f"{i}. {filename}")
            print(f"   大小: {file_size:.2f} MB")
            if metadata.get("prompt"):
                prompt_short = metadata["prompt"][:50] + "..." if len(metadata["prompt"]) > 50 else metadata["prompt"]
                print(f"   提示: {prompt_short}")
            print(f"   路徑: {filepath}")
            print()


def quick_video_generation():
    """快速影片生成"""
    
    saver = VeoVideoSaver()
    
    print("🎬 Veo 影片生成與儲存工具")
    print("=" * 50)
    
    # 預設提示詞選項
    default_prompts = [
        "一隻可愛的橘色小貓在綠色草地上快樂地奔跑，陽光明媚",
        "夕陽西下的海邊，海浪輕柔地拍打沙灘，海鷗在天空中飛翔",
        "櫻花飛舞的公園，微風輕拂，粉色花瓣如雪花般飄落",
        "雨後的森林，陽光透過樹葉灑下，露珠在葉片上閃閃發光",
        "繁華的夜市，五彩霓虹燈閃爍，人群熙熙攘攘"
    ]
    
    print("\n選擇要生成的影片類型:")
    for i, prompt in enumerate(default_prompts, 1):
        print(f"{i}. {prompt}")
    print("6. 自訂提示詞")
    print("7. 查看已儲存的影片")
    
    try:
        choice = input("\n請選擇 (1-7): ").strip()
        
        if choice == "7":
            saver.list_saved_videos()
            return
        
        if choice == "6":
            prompt = input("請輸入您的提示詞: ").strip()
            if not prompt:
                print("❌ 提示詞不能為空")
                return
        else:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(default_prompts):
                prompt = default_prompts[choice_idx]
            else:
                print("❌ 無效選擇")
                return
        
        # 生成並儲存影片
        filepath = saver.generate_and_save_video(prompt)
        
        # 詢問是否開啟影片
        open_choice = input("\n是否要開啟影片播放? (y/n): ").strip().lower()
        if open_choice in ['y', 'yes', '是']:
            saver.open_video(filepath)
        
        print(f"\n✅ 完成！影片儲存於: {filepath}")
        
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
    except Exception as e:
        print(f"❌ 發生錯誤: {str(e)}")


if __name__ == "__main__":
    quick_video_generation()