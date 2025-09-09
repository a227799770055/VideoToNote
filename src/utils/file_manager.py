"""
檔案管理工具
"""
import os
from pathlib import Path
from typing import Optional
from ..core.config import config

class FileManager:
    @staticmethod
    def get_base_name(file_path: str) -> str:
        """取得檔案基本名稱（不含副檔名）"""
        return Path(file_path).stem
    
    @staticmethod
    def generate_output_path(input_path: str, output_dir: Path, suffix: str, extension: str = ".txt") -> Path:
        """
        產生輸出檔案路徑
        
        Args:
            input_path: 輸入檔案路徑
            output_dir: 輸出目錄
            suffix: 檔名後綴
            extension: 副檔名
        """
        base_name = FileManager.get_base_name(input_path)
        filename = f"{base_name}{suffix}{extension}"
        return output_dir / filename
    
    @staticmethod
    def cleanup_file(file_path: str) -> bool:
        """安全地刪除檔案"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已刪除檔案: {file_path}")
                return True
            return False
        except Exception as e:
            print(f"刪除檔案失敗: {e}")
            return False
    
    @staticmethod
    def save_text_file(content: str, file_path: Path) -> bool:
        """儲存文字檔案"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"檔案已儲存到: {file_path}")
            return True
        except Exception as e:
            print(f"儲存檔案失敗: {e}")
            return False
