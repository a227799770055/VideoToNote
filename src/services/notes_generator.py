# -*- coding: utf-8 -*-
"""
筆記生成服務 - 支援多種 AI 模型
"""
import requests
import google.generativeai as genai
from openai import OpenAI
from typing import Optional, Dict, Any
from ..core.config import config
from ..utils.file_manager import FileManager

class NotesGenerator:
    def __init__(self, model_choice: str = 'openai', api_key: Optional[str] = None):
        self.model_choice = model_choice

        if self.model_choice == 'openai':
            self.api_key = api_key or config.OPENAI_API_KEY
            if not self.api_key:
                raise ValueError("OpenAI API Key not found.")
            self.client = OpenAI(api_key=self.api_key)
            self.model_name = config.OPENAI_MODEL
        elif self.model_choice == 'deepseek':
            self.api_key = api_key or config.DEEPSEEK_API_KEY
            if not self.api_key:
                raise ValueError("DeepSeek API Key not found.")
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            self.model_name = config.DEEPSEEK_MODEL
        elif self.model_choice == 'gemini':
            self.api_key = api_key or config.GEMINI_API_KEY
            if not self.api_key:
                raise ValueError("Gemini API Key not found.")
            genai.configure(api_key=self.api_key)
            self.model_name = config.GEMINI_MODEL
        elif self.model_choice == 'ollama':
            self.model_name = config.OLLAMA_MODEL
            self.api_url = config.OLLAMA_API_URL
        else:
            raise ValueError(f"Unsupported model choice: {self.model_choice}")

    def generate_notes(self, transcription: Dict[str, Any], prompt: str = None) -> Optional[str]:
        """
        從轉錄結果生成筆記
        
        Args:
            transcription: 轉錄結果
            prompt: 自定義提示詞
            
        Returns:
            生成的筆記內容
        """
        try:
            if isinstance(transcription, dict) and 'text' in transcription:
                text = transcription['text']
            else:
                text = str(transcription)
            
            prompt = prompt or config.DEFAULT_PROMPT
            full_prompt = f"""{prompt}

逐字稿內容:
{text}"""

            print(f"正在使用 {self.model_choice} 模型生成筆記...")

            if self.model_choice in ['openai', 'deepseek']:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "你是一個專業的筆記整理專家"},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                notes = response.choices[0].message.content
            elif self.model_choice == 'gemini':
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(full_prompt)
                notes = response.text
            elif self.model_choice == 'ollama':
                notes = ""
                try:
                    response = requests.post(
                        self.api_url,
                        json={
                            "model": self.model_name,
                            "prompt": full_prompt,
                            "stream": False
                        }
                    )
                    response.raise_for_status()
                    notes = response.json().get('response', '')
                except requests.exceptions.RequestException as e:
                    print(f"連接 Ollama API 時發生錯誤: {e}")
                    print(f"請確保 Ollama 服務正在運行，並且 API URL ({self.api_url}) 是正確的。")
                    return None
                except Exception as e:
                    print(f"生成筆記時發生錯誤: {e}")
                    return None
            
            return notes
        
        except Exception as e:
            print(f"生成筆記時發生錯誤: {e}")
            return None
        
    def save_notes(self, notes: str, audio_path: str) -> str:
        """
        保存生成的筆記
        
        Args:
            notes: 筆記內容
            audio_path: 原始音檔路徑
            
        Returns:
            保存的檔案路徑
        """
        output_path = FileManager.generate_output_path(
            audio_path, 
            config.NOTES_DIR, 
            "_notes"
        )
        
        if FileManager.save_text_file(notes or "", output_path):
            return str(output_path)
        
        return None
