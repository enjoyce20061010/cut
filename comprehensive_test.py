#!/usr/bin/env python3
"""
Veo API 綜合測試腳本
包含所有支援模型的測試和長時間操作輪詢功能
"""

import os
import json
import time
import requests
import subprocess
from typing import Dict, Any, Optional, List


class VeoComprehensiveClient:
    """Veo API 綜合客戶端，支援所有模型和功能"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1"
        
        # 支援的模型列表
        self.supported_models = {
            "veo-2.0-generate-001": {
                "name": "Veo 2.0 GA版本",
                "supports_audio": False,
                "duration_range": [5, 8],
                "default_duration": 8
            },
            "veo-2.0-generate-exp": {
                "name": "Veo 2.0 實驗版本",
                "supports_audio": False,
                "supports_reference_images": True,
                "duration_range": [5, 8],
                "default_duration": 8
            },
            "veo-3.0-generate-001": {
                "name": "Veo 3.0 標準版本",
                "supports_audio": True,
                "duration_range": [4, 6, 8],
                "default_duration": 8
            },
            "veo-3.0-fast-generate-001": {
                "name": "Veo 3.0 快速版本", 
                "supports_audio": True,
                "duration_range": [4, 6, 8],
                "default_duration": 8
            },
            "veo-3.0-generate-preview": {
                "name": "Veo 3.0 預覽版本",
                "supports_audio": True,
                "duration_range": [4, 6, 8],
                "default_duration": 8,
                "preview": True
            },
            "veo-3.0-fast-generate-preview": {
                "name": "Veo 3.0 快速預覽版本",
                "supports_audio": True,
                "duration_range": [4, 6, 8],
                "default_duration": 8,
                "preview": True
            }
        }
    
    def get_access_token(self) -> str:
        """獲取 Google Cloud 存取權杖"""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"無法獲取存取權杖: {e}")
    
    def list_available_models(self) -> None:
        """列出所有可用的模型"""
        print("📋 支援的 Veo 模型:")
        print("-" * 60)
        
        for model_id, info in self.supported_models.items():
            print(f"🤖 {model_id}")
            print(f"   名稱: {info['name']}")
            print(f"   音訊支援: {'✅' if info.get('supports_audio', False) else '❌'}")
            print(f"   參考圖片: {'✅' if info.get('supports_reference_images', False) else '❌'}")
            print(f"   影片長度: {info['duration_range']} 秒")
            
            if info.get('preview'):
                print(f"   狀態: 🧪 預覽版本")
            print()
    
    def generate_video(
        self,
        prompt: str,
        model_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成影片的通用方法
        
        Args:
            prompt: 文字提示
            model_id: 模型 ID
            **kwargs: 其他參數
        """
        if model_id not in self.supported_models:
            raise ValueError(f"不支援的模型: {model_id}")
        
        model_info = self.supported_models[model_id]
        
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 基本實例資料
        instances = [{"prompt": prompt}]
        
        # 基本參數
        parameters = {
            "aspectRatio": kwargs.get("aspect_ratio", "16:9"),
            "durationSeconds": kwargs.get("duration_seconds", model_info["default_duration"]),
            "sampleCount": kwargs.get("sample_count", 1)
        }
        
        # 儲存位置
        if kwargs.get("storage_uri"):
            parameters["storageUri"] = kwargs["storage_uri"]
        
        # Veo 3 模型的特殊參數
        if "veo-3" in model_id and model_info.get("supports_audio"):
            parameters["generateAudio"] = kwargs.get("generate_audio", True)
            parameters["resolution"] = kwargs.get("resolution", "720p")
        
        # 其他可選參數
        optional_params = [
            "enhancePrompt", "negativePrompt", "personGeneration",
            "compressionQuality", "seed"
        ]
        
        for param in optional_params:
            if param in kwargs:
                parameters[param] = kwargs[param]
        
        payload = {
            "instances": instances,
            "parameters": parameters
        }
        
        print(f"發送請求到模型: {model_id} ({model_info['name']})")
        print(f"請求參數: {json.dumps(parameters, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_details = response.text
            raise Exception(f"API 請求失敗 [{response.status_code}]: {error_details}")
    
    def check_operation_status(self, operation_name: str, model_id: str) -> Dict[str, Any]:
        """檢查長時間運行操作的狀態"""
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:fetchPredictOperation"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {"operationName": operation_name}
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # 顯示詳細狀態信息
            done = result.get("done", False)
            status_text = "完成" if done else "進行中"
            print(f"   狀態: {status_text}")
            
            if done and "response" in result:
                response_data = result["response"]
                filtered_count = response_data.get("raiMediaFilteredCount", 0)
                if filtered_count > 0:
                    print(f"   安全篩選: {filtered_count} 個影片被篩選")
            
            return result
        else:
            raise Exception(f"狀態檢查失敗: {response.status_code} - {response.text}")
    
    def wait_for_completion(
        self,
        operation_name: str,
        model_id: str,
        max_wait_time: int = 300,
        check_interval: int = 15
    ) -> Dict[str, Any]:
        """等待操作完成，並提供進度更新"""
        start_time = time.time()
        last_check_time = 0
        
        print(f"⏳ 等待影片生成完成 (最多 {max_wait_time} 秒)...")
        
        while time.time() - start_time < max_wait_time:
            elapsed = int(time.time() - start_time)
            
            # 定期檢查狀態
            if elapsed - last_check_time >= check_interval:
                status = self.check_operation_status(operation_name, model_id)
                last_check_time = elapsed
                
                if status.get("done", False):
                    print("✅ 影片生成完成!")
                    return status
                
                print(f"   已等待: {elapsed} 秒")
            
            time.sleep(5)  # 每 5 秒檢查一次是否該更新狀態
        
        raise Exception(f"⏰ 操作超時，已等待 {max_wait_time} 秒")
    
    def display_results(self, result: Dict[str, Any]) -> None:
        """顯示生成結果"""
        if "response" not in result:
            print("❌ 沒有回應資料")
            return
        
        response_data = result["response"]
        
        # 安全篩選資訊
        filtered_count = response_data.get("raiMediaFilteredCount", 0)
        if filtered_count > 0:
            print(f"⚠️ 安全篩選: {filtered_count} 個影片因內容政策被篩除")
            
            # 顯示篩選原因（如果有）
            filtered_reasons = response_data.get("raiMediaFilteredReasons", [])
            if filtered_reasons:
                print(f"   篩選原因: {', '.join(filtered_reasons)}")
        
        # 生成的影片
        videos = response_data.get("videos", [])
        if videos:
            print(f"🎥 成功生成 {len(videos)} 個影片:")
            
            for i, video in enumerate(videos, 1):
                print(f"   影片 {i}:")
                
                if "gcsUri" in video:
                    print(f"      雲端儲存: {video['gcsUri']}")
                elif "bytesBase64Encoded" in video:
                    size = len(video["bytesBase64Encoded"])
                    print(f"      Base64 編碼: {size:,} 字符")
                
                mime_type = video.get("mimeType", "未知")
                print(f"      格式: {mime_type}")
        else:
            print("❌ 沒有生成任何影片")


def test_all_models():
    """測試所有支援的模型"""
    
    PROJECT_ID = "gen-lang-client-0510365442"  # 您的專案 ID
    
    if PROJECT_ID == "your-project-id":
        print("⚠️ 請先設定您的 Google Cloud 專案 ID")
        return
    
    # 創建客戶端
    client = VeoComprehensiveClient(PROJECT_ID)
    
    # 顯示支援的模型
    client.list_available_models()
    
    # 測試提示詞
    test_prompts = [
        "一隻橘色小貓在綠色草地上快樂地奔跑，陽光明媚，花朵盛開",
        "未來城市的夜景，霓虹燈閃爍，飛車穿梭於摩天大樓之間",
        "海浪輕柔地拍打著沙灘，夕陽西下，海鷗在天空中自由飛翔"
    ]
    
    # 要測試的模型（從最穩定的開始）
    models_to_test = [
        "veo-2.0-generate-001",
        "veo-3.0-generate-001", 
        "veo-3.0-fast-generate-001"
    ]
    
    for i, model_id in enumerate(models_to_test):
        prompt = test_prompts[i % len(test_prompts)]
        
        print(f"\n{'='*70}")
        print(f"🧪 測試 {i+1}: {model_id}")
        print(f"📝 提示: {prompt}")
        print(f"{'='*70}")
        
        try:
            # 發送生成請求
            result = client.generate_video(
                prompt=prompt,
                model_id=model_id,
                duration_seconds=8,
                sample_count=1,
                aspect_ratio="16:9",
                enhancePrompt=True
            )
            
            operation_name = result.get("name")
            if not operation_name:
                print("❌ 未獲得操作名稱")
                continue
            
            print(f"✅ 請求已提交")
            print(f"   操作 ID: {operation_name.split('/')[-1]}")
            
            # 等待完成
            final_result = client.wait_for_completion(
                operation_name,
                model_id,
                max_wait_time=300
            )
            
            # 顯示結果
            client.display_results(final_result)
            
            print(f"✅ 測試 {i+1} 完成")
            
        except Exception as e:
            print(f"❌ 測試 {i+1} 失敗: {str(e)}")
            # 繼續測試下一個模型
            continue


def quick_test():
    """快速測試單一模型"""
    
    PROJECT_ID = "gen-lang-client-0510365442"  # 設定為用戶的專案 ID
    
    if PROJECT_ID == "your-project-id":
        print("⚠️ 請先設定您的 Google Cloud 專案 ID")
        return
    
    client = VeoComprehensiveClient(PROJECT_ID)
    
    print("🚀 Veo API 快速測試")
    print("使用 veo-3.0-fast-generate-001 模型")
    print()
    
    try:
        result = client.generate_video(
            prompt="一朵美麗的玫瑰花在微風中輕輕搖擺，花瓣晶瑩剔透",
            model_id="veo-3.0-fast-generate-001",
            duration_seconds=6,
            sample_count=1
        )
        
        operation_name = result.get("name")
        print(f"✅ 請求已提交: {operation_name}")
        
        # 等待完成
        final_result = client.wait_for_completion(operation_name, "veo-3.0-fast-generate-001")
        
        # 顯示結果
        client.display_results(final_result)
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")


if __name__ == "__main__":
    print("🎬 Veo API 綜合測試工具")
    print("📋 基於 Google Cloud Vertex AI 官方文檔")
    print()
    
    # 檢查 gcloud 認證
    try:
        subprocess.run(["gcloud", "auth", "list"], capture_output=True, check=True)
        print("✅ Google Cloud CLI 已認證")
        print()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 請先安裝並認證 Google Cloud CLI")
        print("   安裝: https://cloud.google.com/sdk/docs/install")
        print("   認證: gcloud auth login")
        exit(1)
    
    # 選擇測試類型
    print("請選擇測試類型:")
    print("1. 快速測試 (單一模型)")
    print("2. 完整測試 (所有模型)")
    
    choice = input("請輸入選項 (1 或 2): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        test_all_models()
    else:
        print("無效選項，執行快速測試...")
        quick_test()