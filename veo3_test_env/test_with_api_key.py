import requests
import json

# 使用 Google AI Platform 公開 API 測試
API_KEY = "AQ.Ab8RN6Iv8LZLfIaljuIhwByeuTAENtkNo3rp3IUaXjH1UcqiBw"

def test_gemini_with_api_key():
    """測試使用 API 金鑰直接呼叫 Gemini 模型"""
    
    # Gemini 2.5 Flash Lite 端點
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [
            {"parts": [{"text": "Hello! 請用中文回答：你是什麼模型？"}]}
        ]
    }
    
    try:
        print("正在測試 Gemini 2.5 Flash Lite...")
        response = requests.post(url, json=payload)
        
        if response.ok:
            result = response.json()
            if 'candidates' in result:
                content = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API 金鑰有效！")
                print(f"Gemini 回應：{content}")
            else:
                print(f"✅ 請求成功，但回應格式異常：{result}")
        else:
            print(f"❌ 請求失敗：{response.status_code}")
            print(f"錯誤詳情：{response.text}")
            
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

def test_veo_with_api_key():
    """測試是否可用 API 金鑰呼叫 Veo 3"""
    
    # 嘗試 AI Platform API 端點格式
    url = f"https://aiplatform.googleapis.com/v1/publishers/google/models/veo-3.0-fast-generate-001:predict?key={API_KEY}"
    
    payload = {
        "instances": [{"prompt": "航拍视角，未来城市夜景，赛博朋克风格，8 s"}],
        "parameters": {"durationSeconds": 8, "sampleCount": 1}
    }
    
    try:
        print("\n正在測試 Veo 3 API 金鑰存取...")
        response = requests.post(url, json=payload)
        
        if response.ok:
            result = response.json()
            print(f"✅ Veo 3 API 金鑰有效！")
            print(f"回應：{json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Veo 3 請求失敗：{response.status_code}")
            print(f"錯誤詳情：{response.text}")
            
            # 如果是 404，嘗試其他端點
            if response.status_code == 404:
                print("\n🔄 嘗試 generativelanguage API...")
                alt_url = f"https://generativelanguage.googleapis.com/v1/models/veo-3.0-fast-generate-001:generateContent?key={API_KEY}"
                alt_response = requests.post(alt_url, json={"contents": [{"parts": [{"text": "generate video: cyberpunk city at night"}]}]})
                
                if alt_response.ok:
                    print(f"✅ 備用端點成功：{alt_response.json()}")
                else:
                    print(f"❌ 備用端點也失敗：{alt_response.status_code} - {alt_response.text}")
            
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    print("=== Google AI API 金鑰測試 ===")
    
    # 先測試基本的 Gemini 模型
    test_gemini_with_api_key()
    
    # 再測試 Veo 3 存取
    test_veo_with_api_key()