"""
配置檔案 - 統一管理所有設定
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # API Keys (建議使用環境變數)
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    DEEPSEEK_API_KEY: Optional[str] = os.getenv('DEEPSEEK_API_KEY')
    
    # 目錄設定
    MP3_DIR: str = "mp3"
    TRANSCRIPTION_DIR: str = "逐字稿"
    NOTES_DIR: str = "筆記"
    
    # 模型設定
    WHISPER_MODEL_ID: str = "openai/whisper-large-v3"
    DEFAULT_LANGUAGE: str = "chinese"
    
    # 下載設定
    DOWNLOAD_RATE_LIMIT: str = "100K"
    
    # 筆記生成設定
    DEFAULT_PROMPT: str = "這是一場演講的逐字稿，請你幫我整理成6000字的筆記"
    OPENAI_MODEL: str = "gpt-4o-mini"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    def __post_init__(self):
        """確保必要的目錄存在"""
        for directory in [self.MP3_DIR, self.TRANSCRIPTION_DIR, self.NOTES_DIR]:
            os.makedirs(directory, exist_ok=True)

# 全域配置實例
config = Config()
