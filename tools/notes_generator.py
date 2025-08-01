"""
筆記生成模組
"""
import os
from openai import OpenAI
from typing import Optional, Dict, Any
from config import config

class NotesGenerator:
    def __init__(self, openai_api_key: str = None, deepseek_api_key: str = None):
        self.openai_api_key = openai_api_key or config.OPENAI_API_KEY
        self.deepseek_api_key = deepseek_api_key or config.DEEPSEEK_API_KEY
        
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.model_flag = "openai"
            self.model_name = config.OPENAI_MODEL
        elif self.deepseek_api_key:
            self.client = OpenAI(
                api_key=self.deepseek_api_key, 
                base_url="https://api.deepseek.com"
            )
            self.model_flag = "deepseek"
            self.model_name = config.DEEPSEEK_MODEL
        else:
            raise ValueError("需要提供 OpenAI 或 DeepSeek 的 API Key")

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
            # 提取文字內容
            if isinstance(transcription, dict) and 'text' in transcription:
                text = transcription['text']
            else:
                text = str(transcription)
            
            prompt = prompt or config.DEFAULT_PROMPT
            
            print("正在生成筆記...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一個專業的筆記整理專家"},
                    {"role": "user", "content": f"{prompt}\n\n逐字稿內容:\n{text}"}
                ]
            )
            
            notes = response.choices[0].message.content
            print("筆記生成完成")
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
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = f"{config.NOTES_DIR}/{base_name}_notes.txt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(notes if notes else "")
            
        print(f"筆記已保存到: {output_path}")
        return output_path
