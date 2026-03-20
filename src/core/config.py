"""
配置管理 - 統一設定管理 (由 YAML 讀取)
"""
import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "model.yaml"

@dataclass
class Config:
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # 路徑設定
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MP3_DIR: Path = DATA_DIR / "mp3"
    TRANSCRIPTION_DIR: Path = DATA_DIR / "transcriptions"
    NOTES_DIR: Path = DATA_DIR / "notes"
    
    # 模型設定
    WHISPER_MODEL_ID: str = "openai/whisper-small"
    DEFAULT_LANGUAGE: str = "chinese"
    
    # API 設定
    OPENAI_MODEL: str = "gpt-4o-mini"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OLLAMA_MODEL: str = "qwen3"
    OLLAMA_API_URL: str = "http://localhost:11434/api/generate"
    
    # 筆記生成設定
    DEFAULT_PROMPT: str = "這是一場演講的逐字稿，請你幫我整理成6000字的筆記"
    
    def __post_init__(self):
        """初始化後：載入 YAML 與建立必要目錄"""
        self._load_yaml_config()
        self._ensure_directories()

    def _load_yaml_config(self):
        """讀取 YAML 設定檔並寫入設定"""
        if not CONFIG_PATH.exists():
            print(f"警告：找不到設定檔 {CONFIG_PATH}，將使用預設或環境變數金鑰")
            return
            
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f) or {}
                
            api_keys = yaml_data.get('api_keys', {})
            # 優先讀取 YAML，若無則依舊讓 OS 環境變數當成 fallback
            self.OPENAI_API_KEY = api_keys.get('openai') or os.getenv('OPENAI_API_KEY')
            self.DEEPSEEK_API_KEY = api_keys.get('deepseek') or os.getenv('DEEPSEEK_API_KEY')
            self.GEMINI_API_KEY = api_keys.get('gemini') or os.getenv('GEMINI_API_KEY')
            
            # 若 YAML 檔內部還有其他設定亦可在此讀取
            models = yaml_data.get('models', {})
            if 'openai_model' in models: self.OPENAI_MODEL = models['openai_model']
            if 'deepseek_model' in models: self.DEEPSEEK_MODEL = models['deepseek_model']
            if 'gemini_model' in models: self.GEMINI_MODEL = models['gemini_model']
            if 'ollama_model' in models: self.OLLAMA_MODEL = models['ollama_model']
            if 'ollama_api_url' in models: self.OLLAMA_API_URL = models['ollama_api_url']
            
        except Exception as e:
            print(f"讀取 YAML 設定檔時發生錯誤: {e}")

    def _ensure_directories(self):
        for directory in [self.DATA_DIR, self.MP3_DIR, self.TRANSCRIPTION_DIR, self.NOTES_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# 全域設定實例
config = Config()
