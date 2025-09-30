import requests
import json

def test_correct_gemini_api():
    """使用正確的 Gemini API 端點測試"""
    
    # 嘗試不同的 API 金鑰格式
    api_keys_to_test = [
        "AQ.Ab8RN6Iv8LZLfIaljuIhwByeuTAENtkNo3rp3IUaXjH1UcqiBw",
        "AIzaSyDc28Pk6n00BEtUIBqgrg3DGu952PCT1zs"  # 之前測試成功的金鑰
    ]
    
    for i, api_key in enumerate(api_keys_to_test):
        print(f"\n=== 測試 API 金鑰 {i+1} ===")
        
        # 使用 v1beta 版本（支援 API 金鑰）
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {"parts": [{"text": "Hello! 請用中文回答：你是什麼模型？"}]}
            ]
        }
        
        try:
            print(f"測試金鑰：{api_key[:20]}...")
            response = requests.post(url, json=payload)
            
            if response.ok:
                result = response.json()
                if 'candidates' in result:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ API 金鑰有效！")
                    print(f"Gemini 回應：{content}")
                    return api_key  # 返回有效的金鑰
                else:
                    print(f"回應格式異常：{result}")
            else:
                print(f"❌ 請求失敗：{response.status_code}")
                print(f"錯誤：{response.text}")
                
        except Exception as e:
            print(f"❌ 發生錯誤：{e}")
    
    return None

def check_veo_availability(api_key):
    """檢查 Veo 模型是否可用"""
    
    print(f"\n=== 檢查 Veo 模型可用性 ===")
    
    # 列出所有可用模型
    models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(models_url)
        if response.ok:
            models = response.json().get("models", [])
            print("可用模型：")
            
            veo_models = []
            for model in models:
                model_name = model.get("name", "")
                print(f"- {model_name}")
                if "veo" in model_name.lower():
                    veo_models.append(model_name)
            
            if veo_models:
                print(f"\n✅ 找到 Veo 模型：{veo_models}")
            else:
                print(f"\n❌ 未找到 Veo 模型")
                
        else:
            print(f"❌ 無法列出模型：{response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    print("=== Gemini API 金鑰驗證與 Veo 檢查 ===")
    
    # 測試 API 金鑰
    valid_key = test_correct_gemini_api()
    
    if valid_key:
        # 檢查 Veo 可用性
        check_veo_availability(valid_key)
    else:
        print("\n❌ 沒有有效的 API 金鑰，無法繼續測試 Veo")
        print("\n建議：")
        print("1. 檢查您的 API 金鑰是否正確")
        print("2. 前往 https://aistudio.google.com/apikey 重新生成")
        print("3. 確認 API 金鑰已啟用相關權限")