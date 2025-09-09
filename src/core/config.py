"""
配置管理 - 重構後的統一設定管理
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent.parent

@dataclass
class Config:
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    DEEPSEEK_API_KEY: Optional[str] = os.getenv('DEEPSEEK_API_KEY')
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    
    # 路徑設定 (使用 pathlib)
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MP3_DIR: Path = DATA_DIR / "mp3"
    TRANSCRIPTION_DIR: Path = DATA_DIR / "transcriptions"
    NOTES_DIR: Path = DATA_DIR / "notes"
    
    # 模型設定
    WHISPER_MODEL_ID: str = "openai/whisper-large-v3"
    DEFAULT_LANGUAGE: str = "chinese"
    
    # API 設定
    OPENAI_MODEL: str = "gpt-4o-mini"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OLLAMA_MODEL: str = "qwen3"
    OLLAMA_API_URL: str = "http://localhost:11434/api/generate"
    
    # 下載設定
    DOWNLOAD_RATE_LIMIT: str = "100K"
    
    # 筆記生成設定
    DEFAULT_PROMPT: str = "這是一場演講的逐字稿，請你幫我整理成6000字的筆記"
    
    def __post_init__(self):
        """確保必要目錄存在"""
        for directory in [self.DATA_DIR, self.MP3_DIR, self.TRANSCRIPTION_DIR, self.NOTES_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# 全域設定實例
config = Config()
