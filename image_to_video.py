#!/usr/bin/env python3
"""
Veo API Image-to-Video Generation 測試
基於 Google Cloud Vertex AI 官方文檔實現圖片轉影片功能
"""

import os
import json
import base64
import time
import requests
import subprocess
from typing import Dict, Any, Optional


class VeoImageToVideoClient:
    """Veo 圖片轉影片 API 客戶端"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
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
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """將圖片編碼為 Base64 字串"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_mime_type(self, image_path: str) -> str:
        """根據檔案副檔名獲取 MIME 類型"""
        if image_path.lower().endswith('.png'):
            return "image/png"
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            return "image/jpeg"
        else:
            raise ValueError(f"不支援的圖片格式: {image_path}")
    
    def generate_video_from_image(
        self,
        image_path: str,
        prompt: str,
        model_id: str = "veo-3.0-generate-001",
        duration_seconds: int = 8,
        sample_count: int = 1,
        aspect_ratio: str = "16:9",
        storage_uri: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        從圖片和文字提示生成影片
        
        Args:
            image_path: 輸入圖片路徑
            prompt: 文字提示
            model_id: 要使用的模型 ID
            duration_seconds: 影片長度（秒）
            sample_count: 要生成的影片數量
            aspect_ratio: 影片比例
            storage_uri: Cloud Storage 儲存位置
            **kwargs: 其他參數
        """
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 編碼圖片
        base64_image = self.encode_image_to_base64(image_path)
        mime_type = self.get_mime_type(image_path)
        
        # 構建請求資料
        instances = [{
            "prompt": prompt,
            "image": {
                "bytesBase64Encoded": base64_image,
                "mimeType": mime_type
            }
        }]
        
        parameters = {
            "aspectRatio": aspect_ratio,
            "durationSeconds": duration_seconds,
            "sampleCount": sample_count
        }
        
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
        
        print(f"發送圖片轉影片請求")
        print(f"圖片: {image_path} ({mime_type})")
        print(f"提示: {prompt}")
        print(f"模型: {model_id}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API 請求失敗: {response.status_code} - {response.text}")
    
    def generate_video_with_reference_images(
        self,
        prompt: str,
        reference_images: list,
        model_id: str = "veo-2.0-generate-exp",
        duration_seconds: int = 8,
        sample_count: int = 1,
        storage_uri: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用參考圖片生成影片（asset 或 style 類型）
        
        Args:
            prompt: 文字提示
            reference_images: 參考圖片列表，格式為 [{"path": "image.jpg", "type": "asset"}]
            model_id: 模型 ID (目前只支援 veo-2.0-generate-exp)
            duration_seconds: 影片長度
            sample_count: 影片數量
            storage_uri: 儲存位置
        """
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 處理參考圖片
        reference_images_data = []
        for ref_img in reference_images:
            base64_image = self.encode_image_to_base64(ref_img["path"])
            mime_type = self.get_mime_type(ref_img["path"])
            
            reference_images_data.append({
                "image": {
                    "bytesBase64Encoded": base64_image,
                    "mimeType": mime_type
                },
                "referenceType": ref_img["type"]  # "asset" 或 "style"
            })
        
        # 構建請求資料
        instances = [{
            "prompt": prompt,
            "referenceImages": reference_images_data
        }]
        
        parameters = {
            "durationSeconds": duration_seconds,
            "sampleCount": sample_count
        }
        
        if storage_uri:
            parameters["storageUri"] = storage_uri
        
        payload = {
            "instances": instances,
            "parameters": parameters
        }
        
        print(f"發送參考圖片影片生成請求")
        print(f"提示: {prompt}")
        print(f"參考圖片數量: {len(reference_images)}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API 請求失敗: {response.status_code} - {response.text}")
    
    def check_operation_status(self, operation_name: str, model_id: str) -> Dict[str, Any]:
        """檢查操作狀態"""
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:fetchPredictOperation"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {"operationName": operation_name}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"狀態檢查失敗: {response.status_code} - {response.text}")
    
    def wait_for_completion(self, operation_name: str, model_id: str, 
                          max_wait_time: int = 300, check_interval: int = 10) -> Dict[str, Any]:
        """等待操作完成"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = self.check_operation_status(operation_name, model_id)
            
            if status.get("done", False):
                print("✅ 影片生成完成!")
                return status
            
            print(f"⏳ 處理中... (已等待 {int(time.time() - start_time)} 秒)")
            time.sleep(check_interval)
        
        raise Exception(f"操作超時，已等待 {max_wait_time} 秒")


def create_sample_image():
    """創建測試用的簡單圖片"""
    try:
        from PIL import Image, ImageDraw
        
        # 創建一個簡單的測試圖片
        img = Image.new('RGB', (1280, 720), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # 畫一個太陽
        draw.ellipse([50, 50, 150, 150], fill='yellow', outline='orange', width=3)
        
        # 畫一些雲朵
        draw.ellipse([200, 80, 300, 120], fill='white')
        draw.ellipse([220, 70, 320, 110], fill='white')
        
        # 儲存圖片
        image_path = "/Users/jianjunneng/0908test/veo_official_test/test_image.jpg"
        img.save(image_path, 'JPEG')
        print(f"✅ 創建測試圖片: {image_path}")
        return image_path
        
    except ImportError:
        print("❌ 需要安裝 Pillow: pip install Pillow")
        return None


def test_image_to_video():
    """測試圖片轉影片功能"""
    
    PROJECT_ID = "your-project-id"  # 請修改為您的專案 ID
    
    if PROJECT_ID == "your-project-id":
        print("⚠️ 請先設定您的 Google Cloud 專案 ID")
        return
    
    # 創建客戶端
    client = VeoImageToVideoClient(PROJECT_ID)
    
    # 創建或使用測試圖片
    test_image = create_sample_image()
    if not test_image:
        print("❌ 無法創建測試圖片")
        return
    
    # 測試案例
    test_cases = [
        {
            "prompt": "圖片中的場景慢慢動畫化，太陽緩緩移動，雲朵飄移",
            "model": "veo-3.0-generate-001",
            "description": "基本圖片轉影片"
        },
        {
            "prompt": "將這個靜態場景轉換為充滿活力的動畫，加入風的效果",
            "model": "veo-2.0-generate-001", 
            "description": "Veo 2.0 圖片轉影片"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🎬 測試案例 {i}: {test_case['description']}")
        print(f"📝 提示: {test_case['prompt']}")
        print(f"🤖 模型: {test_case['model']}")
        print(f"{'='*60}")
        
        try:
            result = client.generate_video_from_image(
                image_path=test_image,
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
            
            print(f"✅ 請求已提交: {operation_name}")
            
            # 等待完成
            final_result = client.wait_for_completion(
                operation_name,
                test_case["model"],
                max_wait_time=300
            )
            
            # 顯示結果
            if "response" in final_result:
                response_data = final_result["response"]
                videos = response_data.get("videos", [])
                
                for j, video in enumerate(videos, 1):
                    if "gcsUri" in video:
                        print(f"🎥 影片 {j}: {video['gcsUri']}")
                    elif "bytesBase64Encoded" in video:
                        print(f"🎥 影片 {j}: Base64 編碼（{len(video['bytesBase64Encoded'])} 字符）")
            
            print(f"✅ 測試案例 {i} 完成")
            
        except Exception as e:
            print(f"❌ 測試案例 {i} 失敗: {str(e)}")


if __name__ == "__main__":
    print("🚀 Veo API 圖片轉影片測試開始")
    print("📋 基於 Google Cloud Vertex AI 官方文檔")
    print()
    
    test_image_to_video()