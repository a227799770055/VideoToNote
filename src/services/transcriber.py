# -*- coding: utf-8 -*-
"""
語音轉錄服務 - 使用 OpenAI Whisper
"""
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pathlib import Path
from typing import Dict, Any, Optional
from ..core.config import config
from ..utils.file_manager import FileManager

class SpeechTranscriber:
    def __init__(self, model_id: str = None, device: str = None):
        self.model_id = model_id or config.WHISPER_MODEL_ID
        self.device = device if device else ("cuda:0" if torch.cuda.is_available() else "cpu")
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        self._load_model()
        
    def _load_model(self):
        """載入語音辨識模型"""
        print("正在載入語音辨識模型...")
        
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, 
            torch_dtype=self.torch_dtype, 
            low_cpu_mem_usage=True, 
            use_safetensors=True
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(self.model_id)
        
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        
        print("語音辨識模型載入完成")

    def transcribe(self, audio_path: str, language: str = None, return_timestamps: bool = True) -> Optional[Dict[str, Any]]:
        """
        轉錄音檔為文字
        
        Args:
            audio_path: 音檔路徑
            language: 目標語言
            return_timestamps: 是否包含時間戳記
            
        Returns:
            轉錄結果字典
        """
        try:
            language = language or config.DEFAULT_LANGUAGE
            
            print(f"開始轉錄音檔: {audio_path}")
            result = self.pipe(
                audio_path,
                return_timestamps=return_timestamps,
                generate_kwargs={"language": language}
            )
            print("轉錄完成")
            return result
            
        except Exception as e:
            print(f"轉錄過程中發生錯誤: {e}")
            return None

    def save_transcription(self, result: Dict[str, Any], audio_path: str) -> str:
        """
        保存轉錄結果
        
        Args:
            result: 轉錄結果
            audio_path: 原始音檔路徑
            
        Returns:
            保存的檔案路徑
        """
        output_path = FileManager.generate_output_path(
            audio_path, 
            config.TRANSCRIPTION_DIR, 
            "_transcription"
        )
        
        content = result.get('text', str(result)) if isinstance(result, dict) else str(result)
        
        if FileManager.save_text_file(content, output_path):
            return str(output_path)
        
        return None
