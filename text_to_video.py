#!/usr/bin/env python3
"""
Veo 3.0 Text-to-Video Generation API 測試
基於 Google Cloud Vertex AI 官方文檔範例實現

支援的模型:
- veo-2.0-generate-001 (GA版本)
- veo-2.0-generate-exp (實驗版本)
- veo-3.0-generate-001 (最新版本)
- veo-3.0-fast-generate-001 (快速版本)
- veo-3.0-generate-preview (預覽版本)
- veo-3.0-fast-generate-preview (快速預覽版本)
"""

import os
import json
import time
import requests
import subprocess
from typing import Dict, Any, Optional, List


class VeoAPIClient:
    """Veo API 客戶端，基於官方 REST API 文檔"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """
        初始化 Veo API 客戶端
        
        Args:
            project_id: Google Cloud 專案 ID
            location: API 端點位置，預設為 us-central1
        """
        self.project_id = project_id
        self.location = location
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1"
        
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
    
    def generate_video_from_text(
        self,
        prompt: str,
        model_id: str = "veo-3.0-generate-001",
        duration_seconds: int = 8,
        sample_count: int = 1,
        aspect_ratio: str = "16:9",
        storage_uri: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        從文字提示生成影片
        
        Args:
            prompt: 文字提示
            model_id: 要使用的模型 ID
            duration_seconds: 影片長度（秒）
            sample_count: 要生成的影片數量
            aspect_ratio: 影片比例 ("16:9" 或 "9:16")
            storage_uri: Cloud Storage 儲存位置 (可選)
            **kwargs: 其他參數
            
        Returns:
            包含操作資訊的字典
        """
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 構建請求資料
        instances = [{
            "prompt": prompt
        }]
        
        parameters = {
            "aspectRatio": aspect_ratio,
            "durationSeconds": duration_seconds,
            "sampleCount": sample_count
        }
        
        # 新增選用參數
        if storage_uri:
            parameters["storageUri"] = storage_uri
            
        # Veo 3 模型的特殊參數
        if "veo-3" in model_id:
            parameters.setdefault("generateAudio", True)
            parameters.setdefault("resolution", "720p")
        
        # 其他選用參數
        for key, value in kwargs.items():
            if key in ["enhancePrompt", "negativePrompt", "personGeneration", 
                      "compressionQuality", "seed"]:
                parameters[key] = value
        
        payload = {
            "instances": instances,
            "parameters": parameters
        }
        
        print(f"發送請求到: {url}")
        print(f"請求內容: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API 請求失敗: {response.status_code} - {response.text}")
    
    def check_operation_status(self, operation_name: str, model_id: str) -> Dict[str, Any]:
        """
        檢查長時間運行操作的狀態
        
        Args:
            operation_name: 操作的完整名稱
            model_id: 模型 ID
            
        Returns:
            操作狀態資訊
        """
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:fetchPredictOperation"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "operationName": operation_name
        }
        
        print(f"檢查操作狀態: {operation_name}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"狀態檢查失敗: {response.status_code} - {response.text}")
    
    def wait_for_completion(self, operation_name: str, model_id: str, 
                          max_wait_time: int = 300, check_interval: int = 10) -> Dict[str, Any]:
        """
        等待操作完成
        
        Args:
            operation_name: 操作名稱
            model_id: 模型 ID
            max_wait_time: 最大等待時間（秒）
            check_interval: 檢查間隔（秒）
            
        Returns:
            完成後的操作結果
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = self.check_operation_status(operation_name, model_id)
            
            if status.get("done", False):
                print("✅ 影片生成完成!")
                return status
            
            print(f"⏳ 操作進行中... (已等待 {int(time.time() - start_time)} 秒)")
            time.sleep(check_interval)
        
        raise Exception(f"操作超時，已等待 {max_wait_time} 秒")


def test_text_to_video():
    """測試文字轉影片功能"""
    
    # 配置參數 - 設定為用戶的 Google Cloud 專案 ID
    PROJECT_ID = "gen-lang-client-0510365442"
    
    if PROJECT_ID == "your-project-id":
        print("⚠️ 請先設定您的 Google Cloud 專案 ID")
        return
    
    # 創建 API 客戶端
    client = VeoAPIClient(PROJECT_ID)
    
    # 測試提示詞列表
    test_prompts = [
        {
            "prompt": "一隻可愛的小貓在陽光明媚的花園裡玩耍，鮮豔的花朵環繞，微風輕撫",
            "model": "veo-3.0-generate-001"
        },
        {
            "prompt": "快速追蹤鏡頭拍攝的場景：熱鬧的烏托邦式蔓延景象，明亮的霓虹燈、飛車和霧氣，夜晚，鏡頭光暈，體積照明",
            "model": "veo-3.0-fast-generate-001"
        },
        {
            "prompt": "許多有斑點的水母在水下跳動。身體呈透明狀，在深海中會發光",
            "model": "veo-2.0-generate-001"
        }
    ]
    
    for i, test_case in enumerate(test_prompts, 1):
        print(f"\n{'='*60}")
        print(f"🎬 測試案例 {i}: {test_case['model']}")
        print(f"📝 提示: {test_case['prompt']}")
        print(f"{'='*60}")
        
        try:
            # 發送生成請求
            result = client.generate_video_from_text(
                prompt=test_case["prompt"],
                model_id=test_case["model"],
                duration_seconds=8,
                sample_count=1,
                aspect_ratio="16:9",
                enhancePrompt=True
            )
            
            operation_name = result.get("name")
            if not operation_name:
                print("❌ 未獲得操作名稱")
                continue
            
            print(f"✅ 請求已提交，操作名稱: {operation_name}")
            
            # 等待完成
            final_result = client.wait_for_completion(
                operation_name, 
                test_case["model"],
                max_wait_time=300
            )
            
            # 顯示結果
            if "response" in final_result:
                response_data = final_result["response"]
                
                # 檢查篩選的影片數量
                filtered_count = response_data.get("raiMediaFilteredCount", 0)
                if filtered_count > 0:
                    print(f"⚠️ 有 {filtered_count} 個影片因安全原因被篩選")
                
                # 顯示生成的影片
                videos = response_data.get("videos", [])
                for j, video in enumerate(videos, 1):
                    if "gcsUri" in video:
                        print(f"🎥 影片 {j}: {video['gcsUri']}")
                    elif "bytesBase64Encoded" in video:
                        print(f"🎥 影片 {j}: Base64 編碼（{len(video['bytesBase64Encoded'])} 字符）")
                    
                    mime_type = video.get("mimeType", "unknown")
                    print(f"   格式: {mime_type}")
            
            print(f"✅ 測試案例 {i} 完成")
            
        except Exception as e:
            print(f"❌ 測試案例 {i} 失敗: {str(e)}")


if __name__ == "__main__":
    print("🚀 Veo API 文字轉影片測試開始")
    print("📋 基於 Google Cloud Vertex AI 官方文檔")
    print()
    
    # 檢查環境
    try:
        subprocess.run(["gcloud", "auth", "list"], capture_output=True, check=True)
        print("✅ Google Cloud CLI 已認證")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 請先安裝並認證 Google Cloud CLI")
        print("   安裝: https://cloud.google.com/sdk/docs/install")
        print("   認證: gcloud auth login")
        exit(1)
    
    test_text_to_video()