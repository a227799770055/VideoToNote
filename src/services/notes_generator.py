# -*- coding: utf-8 -*-
"""
筆記生成服務 - 支援多種 AI 模型
"""
import requests
import google.generativeai as genai
from openai import OpenAI
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from ..core.config import config
from ..utils.file_manager import FileManager

class BaseNotesGenerator(ABC):
    @abstractmethod
    def generate_notes(self, transcription: Dict[str, Any], prompt: str = None) -> Optional[str]:
        """從轉錄結果生成筆記"""
        pass

    def save_notes(self, notes: str, audio_path: str) -> str:
        """保存生成的筆記"""
        output_path = FileManager.generate_output_path(
            audio_path, 
            config.NOTES_DIR, 
            "_notes"
        )
        if FileManager.save_text_file(notes or "", output_path):
            return str(output_path)
        return None

    def _get_full_prompt(self, transcription: Dict[str, Any], prompt: str = None) -> str:
        text = transcription.get('text', str(transcription)) if isinstance(transcription, dict) else str(transcription)
        prompt = prompt or config.DEFAULT_PROMPT
        return f"{prompt}\n\n逐字稿內容:\n{text}"

class OpenAIGenerator(BaseNotesGenerator):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API Key not found.")
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = config.OPENAI_MODEL

    def generate_notes(self, transcription: Dict[str, Any], prompt: str = None) -> Optional[str]:
        try:
            full_prompt = self._get_full_prompt(transcription, prompt)
            print("正在使用 OpenAI 模型生成筆記...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一個專業的筆記整理專家"},
                    {"role": "user", "content": full_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"生成筆記時發生錯誤: {e}")
            return None

class DeepSeekGenerator(BaseNotesGenerator):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DeepSeek API Key not found.")
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.model_name = config.DEEPSEEK_MODEL

    def generate_notes(self, transcription: Dict[str, Any], prompt: str = None) -> Optional[str]:
        try:
            full_prompt = self._get_full_prompt(transcription, prompt)
            print("正在使用 DeepSeek 模型生成筆記...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一個專業的筆記整理專家"},
                    {"role": "user", "content": full_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"生成筆記時發生錯誤: {e}")
            return None

class GeminiGenerator(BaseNotesGenerator):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API Key not found.")
        genai.configure(api_key=self.api_key)
        self.model_name = config.GEMINI_MODEL

    def generate_notes(self, transcription: Dict[str, Any], prompt: str = None) -> Optional[str]:
        try:
            full_prompt = self._get_full_prompt(transcription, prompt)
            print("正在使用 Gemini 模型生成筆記...")
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"生成筆記時發生錯誤: {e}")
            return None

class OllamaGenerator(BaseNotesGenerator):
    def __init__(self):
        self.model_name = config.OLLAMA_MODEL
        self.api_url = config.OLLAMA_API_URL

    def generate_notes(self, transcription: Dict[str, Any], prompt: str = None) -> Optional[str]:
        try:
            full_prompt = self._get_full_prompt(transcription, prompt)
            print("正在使用 Ollama 模型生成筆記...")
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json().get('response', '')
        except requests.exceptions.RequestException as e:
            print(f"連接 Ollama API 時發生錯誤: {e}")
            return None
        except Exception as e:
            print(f"生成筆記時發生錯誤: {e}")
            return None

class NotesGeneratorFactory:
    @staticmethod
    def create(model_choice: str = 'openai', api_key: Optional[str] = None) -> BaseNotesGenerator:
        model_choice = model_choice.lower()
        if model_choice == 'openai':
            return OpenAIGenerator(api_key=api_key)
        elif model_choice == 'deepseek':
            return DeepSeekGenerator(api_key=api_key)
        elif model_choice == 'gemini':
            return GeminiGenerator(api_key=api_key)
        elif model_choice == 'ollama':
            return OllamaGenerator()
        else:
            raise ValueError(f"Unsupported model choice: {model_choice}")

NotesGenerator = NotesGeneratorFactory
