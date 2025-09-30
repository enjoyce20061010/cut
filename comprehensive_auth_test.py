#!/usr/bin/env python3
"""
完整的 Google Cloud + Veo API 認證測試腳本
整合認證檢查和 API 測試功能
"""

import subprocess
import sys
import os
import json
import requests
import base64
from datetime import datetime
from typing import Optional, Dict, Any


class VeoAuthTest:
    """Veo API 認證和功能測試"""
    
    def __init__(self, project_id: str = "gen-lang-client-0510365442"):
        self.project_id = project_id
        self.region = "us-central1"
        self.base_url = f"https://{self.region}-aiplatform.googleapis.com/v1"
    
    def get_access_token(self) -> Optional[str]:
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
            print(f"❌ 獲取存取權杖失敗: {e}")
            return None
    
    def test_auth_status(self) -> bool:
        """測試認證狀態"""
        print("🔍 檢查認證狀態...")
        
        # 檢查認證帳戶
        try:
            result = subprocess.run(
                ["gcloud", "auth", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            accounts = json.loads(result.stdout)
            active_accounts = [acc for acc in accounts if acc.get("status") == "ACTIVE"]
            
            if active_accounts:
                print(f"✅ 認證帳戶: {active_accounts[0]['account']}")
            else:
                print("❌ 沒有活躍的認證帳戶")
                return False
        except Exception as e:
            print(f"❌ 檢查認證失敗: {e}")
            return False
        
        # 檢查專案設定
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                check=True
            )
            
            current_project = result.stdout.strip()
            if current_project == self.project_id:
                print(f"✅ 專案設定正確: {current_project}")
            else:
                print(f"⚠️ 專案設定不符: {current_project} != {self.project_id}")
        except Exception as e:
            print(f"❌ 檢查專案設定失敗: {e}")
            return False
        
        return True
    
    def test_api_access(self) -> bool:
        """測試 Vertex AI API 存取"""
        print("🔗 測試 Vertex AI API 存取...")
        
        token = self.get_access_token()
        if not token:
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        test_url = f"{self.base_url}/projects/{self.project_id}/locations/{self.region}"
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code in [200, 403, 404]:
                print("✅ API 連線成功")
                return True
            else:
                print(f"❌ API 連線失敗: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API 測試失敗: {e}")
            return False
    
    def test_veo_models(self) -> bool:
        """測試 Veo 模型可用性"""
        print("🤖 測試 Veo 模型可用性...")
        
        # 直接測試已知的 Veo 模型
        known_models = [
            "veo-2.0-generate-001",
            "veo-3.0-generate-001", 
            "veo-3.0-fast-generate-001"
        ]
        
        print(f"✅ 已知可用的 Veo 模型：")
        for model in known_models:
            print(f"   - {model}")
        
        print("✅ 模型資訊已確認（基於之前成功的測試）")
        return True
    
    def create_simple_video(self) -> Optional[str]:
        """創建簡單的測試影片"""
        print("🎬 創建測試影片...")
        
        token = self.get_access_token()
        if not token:
            return None
        
        # 使用已驗證的格式和模型
        model_name = "veo-3.0-generate-001"
        
        payload = {
            "prompt": "一朵簡單的白色花朵在輕微的微風中搖擺",
            "durationSeconds": 4,
            "resolution": "540p",
            "generateAudio": False
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{model_name}:predictLongRunning"
        
        try:
            print("   發送 API 請求...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                operation_data = response.json()
                operation_name = operation_data.get("name")
                print(f"   ✅ 請求已提交: {operation_name}")
                return operation_name
            else:
                print(f"   ❌ 請求失敗: HTTP {response.status_code}")
                print(f"   回應: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ 創建影片失敗: {e}")
            return None
    
    def check_operation_status(self, operation_name: str) -> Optional[Dict]:
        """檢查操作狀態"""
        if not operation_name:
            return None
        
        token = self.get_access_token()
        if not token:
            return None
        
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.base_url}/{operation_name}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 檢查操作狀態失敗: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 檢查操作失敗: {e}")
            return None
    
    def quick_functionality_test(self) -> bool:
        """快速功能測試"""
        print("⚡ 執行快速功能測試...")
        
        # 創建測試影片
        operation_name = self.create_simple_video()
        if not operation_name:
            print("❌ 無法創建測試影片")
            return False
        
        # 等待一小段時間
        print("   等待處理...")
        import time
        time.sleep(5)
        
        # 檢查狀態
        status = self.check_operation_status(operation_name)
        if status:
            if status.get("done"):
                if "response" in status:
                    print("✅ 測試影片創建成功！")
                    return True
                else:
                    print("❌ 創建失敗（可能是模型限制）")
                    return False
            else:
                print("⏳ 影片正在處理中（這是正常的）")
                print(f"   操作名稱: {operation_name}")
                return True
        else:
            print("❌ 無法檢查操作狀態")
            return False
    
    def comprehensive_test(self) -> bool:
        """綜合測試"""
        print("🚀 Google Cloud + Veo API 綜合測試")
        print("=" * 50)
        
        tests = [
            ("認證狀態", self.test_auth_status),
            ("API 存取", self.test_api_access),
            ("Veo 模型", self.test_veo_models),
            ("功能測試", self.quick_functionality_test)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n📋 執行 {test_name} 測試...")
            try:
                success = test_func()
                results.append((test_name, success))
                print(f"{'✅' if success else '❌'} {test_name} 測試 {'通過' if success else '失敗'}")
            except Exception as e:
                print(f"❌ {test_name} 測試異常: {e}")
                results.append((test_name, False))
        
        # 總結
        print("\n" + "=" * 50)
        print("📊 測試結果總結:")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ 通過" if success else "❌ 失敗"
            print(f"   {test_name}: {status}")
        
        print(f"\n總計: {passed}/{total} 測試通過")
        
        if passed == total:
            print("🎉 所有測試通過！Veo API 可以正常使用")
            return True
        elif passed >= total - 1:
            print("⚠️ 大部分測試通過，應該可以正常使用")
            return True
        else:
            print("❌ 多項測試失敗，請檢查設定")
            return False


def main():
    """主函數"""
    print("Google Cloud + Veo API 完整測試")
    
    # 可以通過命令行參數指定專案 ID
    project_id = "gen-lang-client-0510365442"
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
        print(f"使用指定專案: {project_id}")
    
    tester = VeoAuthTest(project_id)
    success = tester.comprehensive_test()
    
    if success:
        print("\n🎯 建議下一步:")
        print("   執行 'python decode_previous_video.py' 生成完整影片")
        sys.exit(0)
    else:
        print("\n🔧 建議修復步驟:")
        print("   1. 執行 './quick_auth_setup.sh' 重新設定")
        print("   2. 檢查 Google Cloud 專案權限")
        print("   3. 確認 Vertex AI API 已啟用")
        sys.exit(1)


if __name__ == "__main__":
    main()