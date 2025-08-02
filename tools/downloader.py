# -*- coding: utf-8 -*-
"""
YouTube 下載器模組
"""
import subprocess
import os
import time
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
                '--verbose', # Keep verbose for now
                '--print', 'filename',
                '--print', 'after_move:filepath',
                '--output-na-placeholder', '', # Add this line
                url
            ]

            print(f"正在下載: {url}")
            print(f"執行命令: {' '.join(command)}")
            
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
            
            # yt-dlp prints the filename of the *original* downloaded file, not necessarily the final mp3
            # We need to parse the title from the output or construct the expected path
            # Extract title from stdout (yt-dlp prints filename on a new line)
            output_lines = result.stdout.strip().split('\n')
            print(f"yt-dlp 輸出: {result.stdout}")
            
            if output_lines:
                # The last line usually contains the filename
                downloaded_filename = output_lines[-1]
                # Remove extension and directory to get just the title
                title = os.path.splitext(os.path.basename(downloaded_filename))[0]
                expected_audio_path = os.path.join(self.output_dir, f"{title}.mp3")
                
                # Wait for the file to exist, with a timeout
                timeout = 60  # seconds - increased timeout for ffmpeg conversion
                start_time = time.time()
                while not os.path.exists(expected_audio_path) and (time.time() - start_time) < timeout:
                    time.sleep(2)  # Check every 2 seconds
                
                if os.path.exists(expected_audio_path):
                    print(f"下載完成: {expected_audio_path}")
                    return expected_audio_path
                else:
                    print(f"下載失敗: 預期的 MP3 檔案未生成或未找到: {expected_audio_path}")
                    # List files in mp3 directory to see what was actually downloaded
                    print(f"mp3 目錄內容:")
                    for file in os.listdir(self.output_dir):
                        print(f"  - {file}")
                    return None
            else:
                print(f"下載失敗: yt-dlp 未返回任何輸出。 Full output: {result.stdout}")
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
