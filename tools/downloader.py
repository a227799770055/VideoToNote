"""
YouTube 下載器模組
"""
import subprocess
import os
from typing import Optional
from config import config

class YouTubeDownloader:
    def __init__(self):
        self.output_dir = config.MP3_DIR
        
    def download_audio(self, url: str) -> Optional[str]:
        """
        下載 YouTube 影片音檔
        
        Args:
            url: YouTube 影片連結
            
        Returns:
            下載的音檔路徑，失敗則返回 None
        """
        try:
            command = [
                'yt-dlp',
                '--throttled-rate', config.DOWNLOAD_RATE_LIMIT,
                '-x',
                '--audio-format', 'mp3',
                '-o', f'{self.output_dir}/%(title)s.%(ext)s',
                '--no-warnings',
                '--print', 'filename',
                url
            ]

            print(f"正在下載: {url}")
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.stderr:
                print(f"警告: {result.stderr}")

            audio_path_raw = result.stdout.strip()
            # yt-dlp 在轉換前打印文件名，因此我們需要將擴展名更改為目標 mp3 格式
            audio_path = os.path.splitext(audio_path_raw)[0] + '.mp3'

            if audio_path and os.path.exists(audio_path):
                print(f"下載完成: {audio_path}")
                return audio_path
            
            print(f"下載失敗: yt-dlp 未返回檔案路徑。 Full output: {result.stdout}")
            return None
            
        except subprocess.CalledProcessError as e:
            self._handle_download_error(e)
            return None
        except Exception as e:
            print(f"發生未預期的錯誤: {str(e)}")
            return None
    
    def _handle_download_error(self, error: subprocess.CalledProcessError):
        """處理下載錯誤"""
        error_msg = error.stderr if error.stderr else error.stdout
        print(f"下載失敗: {error_msg}")
        print("請確保：")
        print("1. 你已經登入 YouTube（在瀏覽器中）")
        print("2. 你的網絡連接正常")
        print("3. 影片是公開可訪問的")
