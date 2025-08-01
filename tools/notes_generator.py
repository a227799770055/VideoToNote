"""
筆記生成模組
"""
import os
import requests
import google.generativeai as genai
from openai import OpenAI
from typing import Optional, Dict, Any
from config import config

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

    def generate_notes(self, transcription: Dict[str, Any}, prompt: str = None) -> Optional[str]:
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
            full_prompt = f"{prompt}

逐字稿內容:
{text}"

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
                response = requests.post(
                    self.api_url,
                    json={
                        "model": self.model_name,
                        "prompt": full_prompt,
                        "stream": False
                    }
                )
                response.raise_for_status() # 如果請求失敗則拋出異常
                notes = response.json().get('response', '')

            print("筆記生成完成")
            return notes
            
        except requests.exceptions.RequestException as e:
            print(f"連接 Ollama API 時發生錯誤: {e}")
            print("請確保 Ollama 服務正在運行，並且 API URL ({self.api_url}) 是正確的。")
            return None
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
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = f"{config.NOTES_DIR}/{base_name}_notes.txt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(notes if notes else "")
            
        print(f"筆記已保存到: {output_path}")
        return output_path
