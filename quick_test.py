#!/usr/bin/env python3
"""
簡化版 Veo API 測試 - 使用服務帳戶金鑰或應用程式預設認證
專案 ID: gen-lang-client-0510365442
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional

class VeoTestClient:
    """簡化版 Veo API 客戶端"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1"
        
        # 模型列表
        self.models = [
            "veo-2.0-generate-001",
            "veo-3.0-generate-001", 
            "veo-3.0-fast-generate-001"
        ]
    
    def get_access_token_from_metadata(self) -> Optional[str]:
        """嘗試從 Compute Engine 元資料服務獲取權杖"""
        try:
            metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
            headers = {"Metadata-Flavor": "Google"}
            
            response = requests.get(metadata_url, headers=headers, timeout=2)
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
        except:
            pass
        return None
    
    def get_access_token_from_gcloud(self) -> Optional[str]:
        """嘗試從 gcloud 獲取權杖"""
        try:
            import subprocess
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return result.stdout.strip()
        except:
            pass
        return None
    
    def get_access_token(self) -> str:
        """嘗試多種方式獲取存取權杖"""
        print("🔑 嘗試獲取 Google Cloud 存取權杖...")
        
        # 方法1: gcloud CLI
        token = self.get_access_token_from_gcloud()
        if token:
            print("✅ 使用 gcloud CLI 認證")
            return token
        
        # 方法2: Compute Engine 元資料
        token = self.get_access_token_from_metadata()
        if token:
            print("✅ 使用 Compute Engine 服務帳戶")
            return token
        
        # 方法3: 環境變數
        if "GOOGLE_ACCESS_TOKEN" in os.environ:
            print("✅ 使用環境變數 GOOGLE_ACCESS_TOKEN")
            return os.environ["GOOGLE_ACCESS_TOKEN"]
        
        raise Exception("""
❌ 無法獲取 Google Cloud 存取權杖！

請選擇以下其中一種認證方式：

1. 安裝並認證 Google Cloud CLI:
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud auth login
   gcloud config set project gen-lang-client-0510365442

2. 設定環境變數（如果您有存取權杖）:
   export GOOGLE_ACCESS_TOKEN="your-token-here"

3. 在 Google Cloud Compute Engine 上運行（自動認證）
        """)
    
    def test_simple_request(self, model_id: str = "veo-3.0-fast-generate-001") -> Dict[str, Any]:
        """發送簡單的測試請求"""
        
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:predictLongRunning"
        
        try:
            access_token = self.get_access_token()
        except Exception as e:
            return {"error": str(e)}
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 簡單的測試請求
        payload = {
            "instances": [{
                "prompt": "一朵美麗的玫瑰花在微風中輕輕搖擺"
            }],
            "parameters": {
                "aspectRatio": "16:9",
                "durationSeconds": 6,
                "sampleCount": 1,
                "generateAudio": True,
                "resolution": "720p"
            }
        }
        
        print(f"🚀 發送測試請求到: {model_id}")
        print(f"📍 端點: {url}")
        print(f"📝 提示: {payload['instances'][0]['prompt']}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            print(f"📡 回應狀態: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                operation_name = result.get("name", "未知")
                print(f"✅ 請求成功提交！")
                print(f"🔄 操作ID: {operation_name.split('/')[-1] if '/' in operation_name else operation_name}")
                return result
            
            else:
                error_text = response.text
                print(f"❌ 請求失敗: {response.status_code}")
                print(f"錯誤詳情: {error_text}")
                
                # 嘗試解析錯誤
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = error_json["error"].get("message", "未知錯誤")
                        print(f"具體錯誤: {error_msg}")
                except:
                    pass
                
                return {"error": f"HTTP {response.status_code}: {error_text}"}
        
        except requests.exceptions.Timeout:
            return {"error": "請求超時，請檢查網路連線"}
        except requests.exceptions.ConnectionError:
            return {"error": "連線錯誤，請檢查網路或端點可用性"}
        except Exception as e:
            return {"error": f"未知錯誤: {str(e)}"}
    
    def test_different_locations(self) -> Dict[str, Any]:
        """測試不同地區的端點"""
        locations = ["us-central1", "us-west1", "europe-west4", "asia-southeast1"]
        
        for location in locations:
            print(f"\n🌍 測試地區: {location}")
            original_location = self.location
            
            try:
                self.location = location
                self.base_url = f"https://{location}-aiplatform.googleapis.com/v1"
                
                result = self.test_simple_request("veo-3.0-fast-generate-001")
                
                if "error" not in result:
                    print(f"✅ 地區 {location} 可用！")
                    return {"working_location": location, "result": result}
                else:
                    print(f"❌ 地區 {location} 不可用: {result['error']}")
            
            except Exception as e:
                print(f"❌ 地區 {location} 測試失敗: {str(e)}")
            
            finally:
                self.location = original_location
                self.base_url = f"https://{original_location}-aiplatform.googleapis.com/v1"
        
        return {"error": "所有測試地區都不可用"}


def main():
    """主測試函數"""
    print("🎬 Veo API 快速測試")
    print(f"📋 專案ID: gen-lang-client-0510365442")
    print("=" * 50)
    
    client = VeoTestClient("gen-lang-client-0510365442")
    
    print("\n🧪 階段 1: 基本連線測試")
    result = client.test_simple_request()
    
    if "error" in result:
        print(f"\n⚠️ 預設地區測試失敗，嘗試其他地區...")
        result = client.test_different_locations()
        
        if "working_location" in result:
            print(f"\n✅ 找到可用地區: {result['working_location']}")
            print("您可以在後續測試中使用此地區")
        else:
            print(f"\n❌ 所有地區測試失敗")
            print("請檢查：")
            print("1. Google Cloud 認證是否正確")
            print("2. 專案是否啟用了 Vertex AI API")
            print("3. 是否有 Veo 模型的存取權限")
            return
    
    print(f"\n🎉 測試完成！")
    print("\n📊 建議的後續步驟：")
    print("1. 如果看到操作ID，表示請求成功提交")
    print("2. 實際影片生成需要等待數分鐘")
    print("3. 使用 comprehensive_test.py 進行完整測試")
    

if __name__ == "__main__":
    main()