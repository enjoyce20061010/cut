#!/usr/bin/env python3
"""
Minimal FastAPI bridge to safely call Veo from a frontend.
Endpoints:
- POST /api/veo/generate -> returns { ok, operationName }
- GET  /api/veo/operations/{operationName} -> returns { ok, done, response }

Auth uses ADC (gcloud auth application-default login) or active gcloud user token.
"""

import os
import time
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import google.auth
from google.auth.transport.requests import Request as GARequest

PROJECT_ID = os.environ.get("VEO_PROJECT_ID", "gen-lang-client-0510365442")
LOCATION = os.environ.get("VEO_LOCATION", "us-central1")
MODEL_ID = os.environ.get("VEO_MODEL_ID", "veo-3.0-fast-generate-001")
BASE_URL = f"https://{LOCATION}-aiplatform.googleapis.com/v1"

app = FastAPI(title="Veo Frontend Bridge", version="1.0")

# Enable permissive CORS for development (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_bearer():
    # Prefer ADC; fallback to gcloud user token
    try:
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        if not creds.valid:
            creds.refresh(GARequest())
        return creds.token
    except Exception:
        # Fallback to gcloud auth print-access-token
        import subprocess
        token = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True, check=True).stdout.strip()
        return token


class GenerateReq(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    durationSeconds: int = Field(6, ge=1, le=60)
    # Basic pattern like "16:9" (two integers separated by colon)
    aspectRatio: str = Field("16:9", pattern=r"^\d+:\d+$")
    sampleCount: int = Field(1, ge=1, le=2)
    generateAudio: bool = True
    # Limit to known-good values supported by the backend
    resolution: str = Field("720p", pattern=r"^(480p|720p|1080p)$")
    # Optional gs:// path if provided
    storageUri: Optional[str] = Field(None, pattern=r"^gs://.+")


class ImageTextGenerateReq(BaseModel):
    prompt: str = Field("", min_length=0, max_length=2000)  # 可選的提示詞
    imageBase64: str = Field(..., min_length=1)  # Base64 編碼的圖片數據
    imageMimeType: str = Field(..., pattern=r"^image/(jpeg|png)$")  # 圖片 MIME 類型
    durationSeconds: int = Field(8, ge=1, le=60)
    aspectRatio: str = Field("16:9", pattern=r"^\d+:\d+$")
    sampleCount: int = Field(1, ge=1, le=2)
    generateAudio: bool = True
    resolution: str = Field("720p", pattern=r"^(480p|720p|1080p)$")
    storageUri: Optional[str] = Field(None, pattern=r"^gs://.+")


@app.post("/api/veo/generate")
def generate(req: GenerateReq):
    url = f"{BASE_URL}/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predictLongRunning"
    headers = {"Authorization": f"Bearer {get_bearer()}", "Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": req.prompt}],
        "parameters": {
            "durationSeconds": req.durationSeconds,
            "sampleCount": req.sampleCount,
            "aspectRatio": req.aspectRatio,
            "generateAudio": req.generateAudio,
            "resolution": req.resolution,
        },
    }
    if req.storageUri:
        payload["parameters"]["storageUri"] = req.storageUri

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "error": r.text}
    op = r.json().get("name")
    return {"ok": True, "operationName": op}


@app.get("/api/veo/operations/{operation_name:path}")
def poll(operation_name: str):
    poll_url = f"{BASE_URL}/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:fetchPredictOperation"
    headers = {"Authorization": f"Bearer {get_bearer()}", "Content-Type": "application/json"}
    r = requests.post(poll_url, headers=headers, json={"operationName": operation_name}, timeout=60)
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "error": r.text}
    data = r.json()
    return {"ok": True, "done": data.get("done", False), "response": data.get("response")}


@app.get("/api/veo/operations")
def poll_query(name: str):
    """Poll using a query string: /api/veo/operations?name=..."""
    return poll(name)


class PollBody(BaseModel):
    operationName: str = Field(..., min_length=1)


@app.post("/api/veo/operations")
def poll_body(body: PollBody):
    """Poll using a JSON body to avoid URL-encoding issues."""
    return poll(body.operationName)


@app.post("/api/veo/generate/wait")
def generate_and_wait(req: GenerateReq):
    """
    Start a generation and wait (poll server-side) until it's done or timeout.
    Returns { ok, done, response, operationName, elapsedSeconds }.
    後端會自動輪詢，生成完成後影片會以 Base64 格式返回，可在前端直接播放或下載。
    """
    url = f"{BASE_URL}/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predictLongRunning"
    headers = {"Authorization": f"Bearer {get_bearer()}", "Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": req.prompt}],
        "parameters": {
            "durationSeconds": req.durationSeconds,
            "sampleCount": req.sampleCount,
            "aspectRatio": req.aspectRatio,
            "generateAudio": req.generateAudio,
            "resolution": req.resolution,
        },
    }
    if req.storageUri:
        payload["parameters"]["storageUri"] = req.storageUri

    start_time = time.time()
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "error": r.text, "elapsedSeconds": int(time.time() - start_time)}
    op = r.json().get("name")

    poll_url = f"{BASE_URL}/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:fetchPredictOperation"
    # 最長等待 5 分鐘，每 3 秒輪詢一次（減少頻率以避免過度請求）
    max_wait_seconds = 300  # 5分鐘
    interval = 3
    waited = 0
    poll_count = 0
    
    while waited <= max_wait_seconds:
        poll_count += 1
        pr = requests.post(poll_url, headers=headers, json={"operationName": op}, timeout=60)
        if pr.status_code != 200:
            return {"ok": False, "status": pr.status_code, "error": pr.text, "operationName": op, "elapsedSeconds": int(time.time() - start_time), "pollCount": poll_count}
        data = pr.json()
        if data.get("done"):
            elapsed = int(time.time() - start_time)
            response = data.get("response", {})
            # 檢查是否有影片資料 - 支持多種可能的結構
            if response:
                # 檢查 videos 結構 (從 decode_previous_video.py 看到的實際結構)
                videos = response.get("videos", [])
                if videos and len(videos) > 0:
                    video = videos[0]
                    if video.get("bytesBase64Encoded"):
                        return {"ok": True, "done": True, "response": response, "operationName": op, "elapsedSeconds": elapsed, "pollCount": poll_count}
                
                # 檢查 predictions 結構 (假設的結構)
                predictions = response.get("predictions", [])
                if predictions and len(predictions) > 0:
                    pred = predictions[0]
                    if pred.get("video") or pred.get("content"):
                        return {"ok": True, "done": True, "response": response, "operationName": op, "elapsedSeconds": elapsed, "pollCount": poll_count}
            
            # 如果沒有影片資料，返回錯誤
            return {"ok": False, "error": "生成完成但未找到影片資料", "response": response, "operationName": op, "elapsedSeconds": elapsed, "pollCount": poll_count}
        time.sleep(interval)
        waited += interval

    # 超時：回前端 operationName 讓前端看要不要繼續查
    elapsed = int(time.time() - start_time)
    return {"ok": True, "done": False, "operationName": op, "elapsedSeconds": elapsed, "pollCount": poll_count, "timeout": True}


@app.post("/api/veo/generate/image-text/wait")
def generate_image_text_and_wait(req: ImageTextGenerateReq):
    """
    從圖片和文字提示生成影片，等待完成後返回結果。
    Returns { ok, done, response, operationName, elapsedSeconds }.
    圖片以 Base64 格式傳入，生成完成後影片會以 Base64 格式返回。
    """
    # 使用圖片轉影片的模型
    image_model_id = "veo-3.0-generate-001"  # 圖片轉影片模型

    url = f"{BASE_URL}/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{image_model_id}:predictLongRunning"
    headers = {"Authorization": f"Bearer {get_bearer()}", "Content-Type": "application/json"}

    # 構建請求 payload - 參考 image_to_video.py 的結構
    instances = [{
        "prompt": req.prompt or "讓圖片中的場景動畫化，加入自然的動態效果",
        "image": {
            "bytesBase64Encoded": req.imageBase64,
            "mimeType": req.imageMimeType
        }
    }]

    parameters = {
        "aspectRatio": req.aspectRatio,
        "durationSeconds": req.durationSeconds,
        "sampleCount": req.sampleCount,
        "generateAudio": req.generateAudio,
        "resolution": req.resolution,
    }

    # Veo 3 模型的特殊參數處理
    if "veo-3" in image_model_id:
        parameters.setdefault("generateAudio", True)
        parameters.setdefault("resolution", "720p")

    if req.storageUri:
        parameters["storageUri"] = req.storageUri

    payload = {
        "instances": instances,
        "parameters": parameters
    }

    start_time = time.time()
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "error": r.text, "elapsedSeconds": int(time.time() - start_time)}

    op = r.json().get("name")
    if not op:
        return {"ok": False, "error": "無法獲取操作名稱", "elapsedSeconds": int(time.time() - start_time)}

    # 輪詢等待完成
    poll_url = f"{BASE_URL}/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{image_model_id}:fetchPredictOperation"
    max_wait_seconds = 300  # 5分鐘
    interval = 3
    waited = 0
    poll_count = 0

    while waited <= max_wait_seconds:
        poll_count += 1
        pr = requests.post(poll_url, headers=headers, json={"operationName": op}, timeout=60)
        if pr.status_code != 200:
            return {"ok": False, "status": pr.status_code, "error": pr.text, "operationName": op, "elapsedSeconds": int(time.time() - start_time), "pollCount": poll_count}

        data = pr.json()
        if data.get("done"):
            elapsed = int(time.time() - start_time)
            response = data.get("response", {})

            # 檢查是否有影片資料
            if response:
                videos = response.get("videos", [])
                if videos and len(videos) > 0:
                    video = videos[0]
                    if video.get("bytesBase64Encoded"):
                        return {"ok": True, "done": True, "response": response, "operationName": op, "elapsedSeconds": elapsed, "pollCount": poll_count}

                # 檢查 predictions 結構 (備用)
                predictions = response.get("predictions", [])
                if predictions and len(predictions) > 0:
                    pred = predictions[0]
                    if pred.get("video") or pred.get("content"):
                        return {"ok": True, "done": True, "response": response, "operationName": op, "elapsedSeconds": elapsed, "pollCount": poll_count}

            # 如果沒有影片資料，返回錯誤
            return {"ok": False, "error": "生成完成但未找到影片資料", "response": response, "operationName": op, "elapsedSeconds": elapsed, "pollCount": poll_count}

        time.sleep(interval)
        waited += interval

    # 超時
    elapsed = int(time.time() - start_time)
    return {"ok": True, "done": False, "operationName": op, "elapsedSeconds": elapsed, "pollCount": poll_count, "timeout": True}
