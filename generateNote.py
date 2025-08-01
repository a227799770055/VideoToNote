import subprocess
import os
from processor import VideoProcessor

def download_youtube_audio(url):
    """向後相容的函數 - 使用新的 VideoProcessor"""
    from tools import YouTubeDownloader
    downloader = YouTubeDownloader()
    return downloader.download_audio(url)

def process_video(url, openai_api_key=None, deepseek_api_key=None):
    """向後相容的函數 - 使用新的 VideoProcessor"""
    try:
        processor = VideoProcessor(
            openai_api_key=openai_api_key,
            deepseek_api_key=deepseek_api_key
        )
        
        success = processor.process_youtube_video(url, keep_audio=False)
        if success:
            print("\n所有處理已完成！")
        else:
            print("\n處理失敗！")
        
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    # 此為測試區塊。
    # API 金鑰應透過 .env 檔案或環境變數設定，請參考 README.md。
    # processor 會自動從設定檔 (config.py) 讀取金鑰。
    
    # 測試用的 YouTube URL
    url = ["https://www.youtube.com/watch?v=-7ObDTOPlZU"]
    for u in url:
        # 處理器會自動使用環境中設定的金鑰
        process_video(u)