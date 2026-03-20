# -*- coding: utf-8 -*-
"""
語音轉錄服務 - 使用 OpenAI Whisper
"""
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from ..core.config import config
from ..utils.file_manager import FileManager

try:
    from pywhispercpp.model import Model as WhisperCppModel
    PYWHISPERCPP_AVAILABLE = True
except ImportError:
    PYWHISPERCPP_AVAILABLE = False

class BaseTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, language: str = None, return_timestamps: bool = True) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def save_transcription(self, result: Dict[str, Any], audio_path: str) -> str:
        pass


class SpeechTranscriber(BaseTranscriber):
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


class FastSpeechTranscriber(BaseTranscriber):
    """
    使用 pywhispercpp 的快速語音轉錄服務
    功能完全對照 SpeechTranscriber，但使用 C++ 實現以獲得更好的性能
    """
    
    def __init__(self, model_id: str = None, device: str = None):
        """
        初始化快速語音轉錄器
        
        Args:
            model_id: 模型名稱 (tiny, base, small, medium, large)
            device: 設備參數 (在 pywhispercpp 中不直接使用，但保持介面一致性)
        """
        if not PYWHISPERCPP_AVAILABLE:
            raise ImportError("pywhispercpp 未安裝。請執行: pip install pywhispercpp")
        
        # 將 Hugging Face 模型名稱對應到 pywhispercpp 模型名稱
        model_mapping = {
            "openai/whisper-tiny": "tiny",
            "openai/whisper-base": "base", 
            "openai/whisper-small": "small",
            "openai/whisper-medium": "medium",
            "openai/whisper-large": "large-v3",  # 修正：使用 large-v3
            "openai/whisper-large-v2": "large-v2",
            "openai/whisper-large-v3": "large-v3"
        }
        
        self.model_id = model_id or config.WHISPER_MODEL_ID
        self.device = device  # 保持介面一致性
        
        # 轉換模型名稱
        if self.model_id in model_mapping:
            self.cpp_model_name = model_mapping[self.model_id]
        else:
            # 如果是直接指定的 cpp 模型名稱，檢查是否有效
            available_models = [
                'base', 'base-q5_1', 'base-q8_0', 'base.en', 'base.en-q5_1', 'base.en-q8_0',
                'large-v1', 'large-v2', 'large-v2-q5_0', 'large-v2-q8_0', 'large-v3', 
                'large-v3-q5_0', 'large-v3-turbo', 'large-v3-turbo-q5_0', 'large-v3-turbo-q8_0',
                'medium', 'medium-q5_0', 'medium-q8_0', 'medium.en', 'medium.en-q5_0', 'medium.en-q8_0',
                'small', 'small-q5_1', 'small-q8_0', 'small.en', 'small.en-q5_1', 'small.en-q8_0',
                'tiny', 'tiny-q5_1', 'tiny-q8_0', 'tiny.en', 'tiny.en-q5_1', 'tiny.en-q8_0'
            ]
            
            specified_model = model_id or "small"
            if specified_model in available_models:
                self.cpp_model_name = specified_model
            else:
                print(f"警告: 模型 '{specified_model}' 不可用，使用預設模型 'small'")
                self.cpp_model_name = "small"
        
        self._load_model()
        
    def _load_model(self):
        """載入語音辨識模型"""
        print("正在載入快速語音辨識模型...")
        print(f"嘗試載入模型: {self.cpp_model_name}")
        
        try:
            self.model = WhisperCppModel(self.cpp_model_name)
            print("快速語音辨識模型載入完成")
        except Exception as e:
            print(f"載入模型 '{self.cpp_model_name}' 失敗: {e}")
            print("嘗試使用備用模型 'base'...")
            try:
                self.model = WhisperCppModel("base")
                self.cpp_model_name = "base"
                print("使用備用模型 'base' 載入完成")
            except Exception as e2:
                print(f"載入備用模型也失敗: {e2}")
                print("嘗試使用最小模型 'tiny'...")
                try:
                    self.model = WhisperCppModel("tiny")
                    self.cpp_model_name = "tiny"
                    print("使用最小模型 'tiny' 載入完成")
                except Exception as e3:
                    print(f"所有模型載入都失敗: {e3}")
                    raise RuntimeError("無法載入任何 Whisper 模型，請檢查 pywhispercpp 安裝")

    def transcribe(self, audio_path: str, language: str = None, return_timestamps: bool = True) -> Optional[Dict[str, Any]]:
        """
        轉錄音檔為文字
        
        Args:
            audio_path: 音檔路徑
            language: 目標語言
            return_timestamps: 是否包含時間戳記
            
        Returns:
            轉錄結果字典，格式與 SpeechTranscriber 一致
        """
        try:
            language = language or config.DEFAULT_LANGUAGE
            
            print(f"開始轉錄音檔: {audio_path}")
            
            # 使用 pywhispercpp 進行轉錄
            segments = self.model.transcribe(audio_path, language=language)
            
            # 組織結果以匹配 SpeechTranscriber 的輸出格式
            full_text = ""
            chunks = []
            
            for segment in segments:
                full_text += segment.text + " "
                
                if return_timestamps:
                    chunk = {
                        "timestamp": [segment.t0, segment.t1],  # 修正：使用 t0, t1 而非 start, end
                        "text": segment.text
                    }
                    chunks.append(chunk)
            
            result = {
                "text": full_text.strip()
            }
            
            if return_timestamps:
                result["chunks"] = chunks
            
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
            "_transcription_fast"
        )
        
        content = result.get('text', str(result)) if isinstance(result, dict) else str(result)
        
        if FileManager.save_text_file(content, output_path):
            return str(output_path)
        
        return None


class TranscriberFactory:
    @staticmethod
    def create(transcriber_type: str = 'fast', **kwargs) -> BaseTranscriber:
        if transcriber_type.lower() == 'fast':
            if PYWHISPERCPP_AVAILABLE:
                return FastSpeechTranscriber(**kwargs)
            else:
                print("快速轉錄器不可用，回退到標準轉錄器")
                return SpeechTranscriber(**kwargs)
        elif transcriber_type.lower() == 'standard':
            return SpeechTranscriber(**kwargs)
        else:
            raise ValueError(f"不支援的轉錄器類型: {transcriber_type}")
