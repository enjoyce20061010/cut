#!/usr/bin/env python3
"""
單元測試：驗證 Base64VideoDecoder.save_base64_video 能寫出 MP4 檔案
- 使用極小的測試 Base64 資料（不是有效影片，但可驗證寫檔流程）
- 將輸出導向專案內的 ./veo_videos 目錄
- 成功條件：檔案存在且大小 > 0，最後清理檔案
"""

import os
import base64
import importlib.util
from pathlib import Path

# 動態載入 decode_previous_video.py 的 Base64VideoDecoder
SPEC = importlib.util.spec_from_file_location(
    "decode_previous_video", str(Path(__file__).with_name("decode_previous_video.py"))
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def test_save_base64_video_to_repo_folder():
    decoder = mod.Base64VideoDecoder()
    # 覆蓋輸出目錄到專案內的 ./veo_videos
    repo_output = Path(__file__).with_name("veo_videos")
    repo_output.mkdir(exist_ok=True)
    decoder.output_dir = str(repo_output)

    # 建立一個很小的 Base64 測試資料（非有效 MP4，只測試寫檔）
    dummy_bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"  # 常見 MP4 header 片段
    dummy_b64 = base64.b64encode(dummy_bytes).decode("utf-8")

    filepath = decoder.save_base64_video(dummy_b64, filename_prefix="unit_test")
    assert os.path.exists(filepath), "輸出檔案不存在"
    assert os.path.getsize(filepath) > 0, "輸出檔案大小應大於 0"

    # 清理
    os.remove(filepath)
    print("✅ 單元測試通過：檔案寫入/刪除流程正常")


if __name__ == "__main__":
    test_save_base64_video_to_repo_folder()
