# -*- coding: utf-8 -*-
"""
YouTube 下載服務
"""
import subprocess
import os
import time
from pathlib import Path
from typing import Optional
from ..core.config import config
from ..utils.file_manager import FileManager

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
                '--verbose',
                '--print', 'filename',
                '--print', 'after_move:filepath',
                '--output-na-placeholder', '',
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
            
            # 解析下載的檔案路徑
            output_lines = result.stdout.strip().split('\n')
            print(f"yt-dlp 輸出: {result.stdout}")
            
            if output_lines:
                downloaded_filename = output_lines[-1]
                title = os.path.splitext(os.path.basename(downloaded_filename))[0]
                expected_audio_path = self.output_dir / f"{title}.mp3"
                
                # 等待檔案生成完成
                timeout = 60
                start_time = time.time()
                while not expected_audio_path.exists() and (time.time() - start_time) < timeout:
                    time.sleep(2)
                
                if expected_audio_path.exists():
                    print(f"下載完成: {expected_audio_path}")
                    return str(expected_audio_path)
                else:
                    print(f"下載失敗: 預期的 MP3 檔案未生成或未找到: {expected_audio_path}")
                    print("mp3 目錄內容:")
                    for file in self.output_dir.iterdir():
                        print(f"  - {file.name}")
                    return None
            else:
                print(f"下載失敗: yt-dlp 未返回任何輸出。完整輸出: {result.stdout}")
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
