#!/usr/bin/env python3
"""
Google Cloud CLI 自動化認證設定腳本
包含安裝檢查、認證流程引導和專案設定
"""

import subprocess
import sys
import os
import json
import platform
from typing import Optional, Dict, Any


class GoogleCloudAuthSetup:
    """Google Cloud 認證自動化設定"""
    
    def __init__(self, project_id: str = "gen-lang-client-0510365442"):
        self.project_id = project_id
        self.system = platform.system()
        
    def check_gcloud_installed(self) -> bool:
        """檢查 gcloud CLI 是否已安裝"""
        try:
            result = subprocess.run(
                ["gcloud", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            print("✅ Google Cloud CLI 已安裝")
            print(f"版本資訊:\n{result.stdout}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Google Cloud CLI 未安裝")
            return False
    
    def install_gcloud_guide(self):
        """提供安裝指引"""
        print("\n🔧 Google Cloud CLI 安裝指引:")
        print("=" * 50)
        
        if self.system == "Darwin":  # macOS
            print("macOS 安裝方式:")
            print("1. 使用 Homebrew (推薦):")
            print("   brew install --cask google-cloud-sdk")
            print("\n2. 手動安裝:")
            print("   https://cloud.google.com/sdk/docs/install-sdk")
            
        elif self.system == "Linux":
            print("Linux 安裝方式:")
            print("1. 使用包管理器:")
            print("   # Ubuntu/Debian")
            print("   sudo apt-get install google-cloud-cli")
            print("\n2. 手動安裝:")
            print("   https://cloud.google.com/sdk/docs/install-sdk")
            
        elif self.system == "Windows":
            print("Windows 安裝方式:")
            print("1. 下載安裝程式:")
            print("   https://cloud.google.com/sdk/docs/install-sdk")
            
        print(f"\n安裝完成後請重新運行此腳本")
    
    def auto_install_macos(self) -> bool:
        """macOS 自動安裝 (需要 Homebrew)"""
        if self.system != "Darwin":
            return False
            
        try:
            # 檢查 Homebrew
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            print("✅ 找到 Homebrew，開始自動安裝...")
            
            # 安裝 Google Cloud CLI
            result = subprocess.run(
                ["brew", "install", "--cask", "google-cloud-sdk"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Google Cloud CLI 安裝成功！")
                return True
            else:
                print(f"❌ 安裝失敗: {result.stderr}")
                return False
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ 未找到 Homebrew，請手動安裝")
            return False
    
    def check_current_auth(self) -> Optional[Dict[str, Any]]:
        """檢查目前認證狀態"""
        try:
            # 檢查認證帳戶
            result = subprocess.run(
                ["gcloud", "auth", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            accounts = json.loads(result.stdout)
            
            if not accounts:
                print("❌ 尚未認證任何 Google 帳戶")
                return None
            
            active_account = None
            for account in accounts:
                if account.get("status") == "ACTIVE":
                    active_account = account
                    break
            
            if active_account:
                print(f"✅ 目前已認證帳戶: {active_account['account']}")
                return active_account
            else:
                print("❌ 沒有啟用的認證帳戶")
                return None
                
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"❌ 檢查認證狀態失敗: {e}")
            return None
    
    def check_project_config(self) -> Optional[str]:
        """檢查專案設定"""
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                check=True
            )
            
            current_project = result.stdout.strip()
            
            if current_project and current_project != "(unset)":
                print(f"✅ 目前專案: {current_project}")
                return current_project
            else:
                print("❌ 尚未設定專案")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ 檢查專案設定失敗: {e}")
            return None
    
    def set_project(self) -> bool:
        """設定專案 ID"""
        try:
            result = subprocess.run(
                ["gcloud", "config", "set", "project", self.project_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ 專案已設定為: {self.project_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 設定專案失敗: {e}")
            return False
    
    def perform_auth_login(self) -> bool:
        """執行認證登入（互動式）"""
        print("\n🔐 開始 Google Cloud 認證...")
        print("這將開啟瀏覽器，請使用您的 Google 帳戶登入")
        
        input("按 Enter 鍵繼續...")
        
        try:
            result = subprocess.run(
                ["gcloud", "auth", "login"],
                check=True
            )
            
            print("✅ 認證成功！")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 認證失敗: {e}")
            return False
    
    def enable_apis(self) -> bool:
        """啟用必要的 API"""
        apis = [
            "aiplatform.googleapis.com",
            "compute.googleapis.com"
        ]
        
        print("\n🔧 啟用必要的 Google Cloud API...")
        
        for api in apis:
            try:
                print(f"   啟用 {api}...")
                subprocess.run(
                    ["gcloud", "services", "enable", api],
                    capture_output=True,
                    check=True
                )
                print(f"   ✅ {api} 已啟用")
                
            except subprocess.CalledProcessError as e:
                print(f"   ❌ 啟用 {api} 失敗: {e}")
                return False
        
        return True
    
    def test_auth(self) -> bool:
        """測試認證是否正常工作"""
        print("\n🧪 測試認證...")
        
        try:
            # 測試存取權杖
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                check=True
            )
            
            token = result.stdout.strip()
            if len(token) > 50:  # 有效的 token 通常很長
                print("✅ 存取權杖獲取成功")
                
                # 測試 API 呼叫
                import requests
                headers = {"Authorization": f"Bearer {token}"}
                test_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1"
                
                response = requests.get(test_url, headers=headers, timeout=10)
                if response.status_code in [200, 403, 404]:  # 能夠連接到 API
                    print("✅ API 連線測試成功")
                    return True
                else:
                    print(f"⚠️ API 回應異常: {response.status_code}")
                    return False
            else:
                print("❌ 存取權杖無效")
                return False
                
        except Exception as e:
            print(f"❌ 認證測試失敗: {e}")
            return False
    
    def create_service_account_guide(self):
        """服務帳戶設定指引（進階選項）"""
        print("\n🤖 服務帳戶設定（進階選項）:")
        print("=" * 50)
        print("如果您想要完全自動化（不需瀏覽器登入），可以使用服務帳戶：")
        print("\n1. 在 Google Cloud Console 中:")
        print("   - 前往 IAM & Admin > Service Accounts")
        print("   - 建立新的服務帳戶")
        print("   - 下載 JSON 金鑰檔案")
        print("\n2. 設定環境變數:")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        print("\n3. 或在 Python 中設定:")
        print("   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/key.json'")
    
    def full_setup(self) -> bool:
        """完整設定流程"""
        print("🚀 Google Cloud CLI 自動化設定")
        print("=" * 50)
        print(f"目標專案 ID: {self.project_id}")
        print()
        
        # 步驟 1: 檢查安裝
        if not self.check_gcloud_installed():
            print("\n🤔 是否要自動安裝 Google Cloud CLI？")
            
            if self.system == "Darwin":
                choice = input("輸入 'y' 自動安裝 (需要 Homebrew) 或 'n' 手動安裝: ").strip().lower()
                if choice == 'y':
                    if not self.auto_install_macos():
                        self.install_gcloud_guide()
                        return False
                else:
                    self.install_gcloud_guide()
                    return False
            else:
                self.install_gcloud_guide()
                return False
        
        # 步驟 2: 檢查認證
        auth_info = self.check_current_auth()
        if not auth_info:
            print("\n🔐 需要進行 Google Cloud 認證")
            if not self.perform_auth_login():
                return False
        
        # 步驟 3: 設定專案
        current_project = self.check_project_config()
        if current_project != self.project_id:
            print(f"\n📋 設定專案為: {self.project_id}")
            if not self.set_project():
                return False
        
        # 步驟 4: 啟用 API
        if not self.enable_apis():
            print("⚠️ 部分 API 啟用失敗，但可能不影響使用")
        
        # 步驟 5: 測試認證
        if not self.test_auth():
            print("⚠️ 認證測試失敗，請檢查設定")
            return False
        
        print("\n🎉 設定完成！")
        print("現在您可以使用 Veo API 了")
        
        # 顯示服務帳戶選項
        show_sa = input("\n是否要查看服務帳戶設定指引？(y/n): ").strip().lower()
        if show_sa == 'y':
            self.create_service_account_guide()
        
        return True


def main():
    """主函數"""
    
    # 可以在這裡修改專案 ID
    PROJECT_ID = "gen-lang-client-0510365442"
    
    # 也可以通過命令行參數指定
    if len(sys.argv) > 1:
        PROJECT_ID = sys.argv[1]
        print(f"使用指定的專案 ID: {PROJECT_ID}")
    
    setup = GoogleCloudAuthSetup(PROJECT_ID)
    success = setup.full_setup()
    
    if success:
        print("\n✅ 所有設定完成，可以開始使用 Veo API！")
        sys.exit(0)
    else:
        print("\n❌ 設定未完成，請檢查上述錯誤訊息")
        sys.exit(1)


if __name__ == "__main__":
    main()