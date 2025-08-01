"""
主要處理流程 - 統合所有功能
"""
import os
from typing import List, Optional
from tools import YouTubeDownloader, SpeechTranscriber, NotesGenerator
from config import config

class VideoProcessor:
    def __init__(self, openai_api_key: str = None, deepseek_api_key: str = None):
        self.downloader = YouTubeDownloader()
        self.transcriber = SpeechTranscriber()
        self.notes_generator = NotesGenerator(
            openai_api_key=openai_api_key,
            deepseek_api_key=deepseek_api_key
        )
        
    def process_youtube_video(self, url: str, keep_audio: bool = False) -> bool:
        """
        處理單一 YouTube 影片
        
        Args:
            url: YouTube 影片連結
            keep_audio: 是否保留音檔
            
        Returns:
            處理是否成功
        """
        print(f"\n處理影片: {url}")
        
        # 1. 下載音檔
        audio_path = self.downloader.download_audio(url)
        if not audio_path:
            print("下載失敗，跳過此影片")
            return False
        
        try:
            # 2. 轉錄
            transcription = self.transcriber.transcribe(audio_path)
            if not transcription:
                print("轉錄失敗")
                return False
            
            # 3. 保存轉錄結果
            transcription_path = self.transcriber.save_transcription(transcription, audio_path)
            
            # 4. 生成筆記
            notes = self.notes_generator.generate_notes(transcription)
            if notes:
                notes_path = self.notes_generator.save_notes(notes, audio_path)
            else:
                print("生成筆記失敗")
            
            # 5. 清理臨時檔案
            if not keep_audio:
                self._cleanup_audio_file(audio_path)
            
            print("影片處理完成！")
            return True
            
        except Exception as e:
            print(f"處理影片時出錯: {e}")
            # 清理臨時檔案
            if not keep_audio:
                self._cleanup_audio_file(audio_path)
            return False
    
    def process_audio_file(self, audio_path: str) -> bool:
        """
        處理本地音檔
        
        Args:
            audio_path: 本地音檔路徑
            
        Returns:
            處理是否成功
        """
        print(f"\n處理音檔: {audio_path}")
        
        if not os.path.exists(audio_path):
            print("音檔不存在")
            return False
        
        try:
            # 1. 轉錄
            transcription = self.transcriber.transcribe(audio_path)
            if not transcription:
                print("轉錄失敗")
                return False
            
            # 2. 保存轉錄結果
            transcription_path = self.transcriber.save_transcription(transcription, audio_path)
            
            # 3. 生成筆記
            notes = self.notes_generator.generate_notes(transcription)
            if notes:
                notes_path = self.notes_generator.save_notes(notes, audio_path)
            else:
                print("生成筆記失敗")
            
            print("音檔處理完成！")
            return True
            
        except Exception as e:
            print(f"處理音檔時出錯: {e}")
            return False
    
    def process_multiple_videos(self, urls: List[str], keep_audio: bool = False) -> List[bool]:
        """
        批次處理多個 YouTube 影片
        
        Args:
            urls: YouTube 影片連結列表
            keep_audio: 是否保留音檔
            
        Returns:
            每個影片的處理結果列表
        """
        results = []
        for url in urls:
            result = self.process_youtube_video(url, keep_audio)
            results.append(result)
        
        successful = sum(results)
        total = len(results)
        print(f"\n批次處理完成！成功: {successful}/{total}")
        return results
    
    def _cleanup_audio_file(self, audio_path: str):
        """清理臨時音檔"""
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"已刪除臨時文件: {audio_path}")
        except Exception as e:
            print(f"刪除臨時文件時出錯: {e}")

# 為了向後相容，保留原來的 SpeechRecognizer 類別
class SpeechRecognizer(VideoProcessor):
    """向後相容的類別名稱"""
    pass
