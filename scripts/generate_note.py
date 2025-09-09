#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
獨立筆記生成腳本 - 從逐字稿生成筆記
"""
import sys
from pathlib import Path

# 將 src 目錄加入 Python 路徑
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.services.notes_generator import NotesGenerator
from src.core.config import config

def main():
    if len(sys.argv) < 2:
        print("用法: python generate_note.py <逐字稿路徑> [模型選擇]")
        print("模型選擇: openai, deepseek, gemini, ollama (預設: openai)")
        sys.exit(1)
    
    transcription_path = sys.argv[1]
    model_choice = sys.argv[2] if len(sys.argv) > 2 else 'openai'
    
    if not Path(transcription_path).exists():
        print(f"錯誤: 逐字稿檔案不存在 - {transcription_path}")
        sys.exit(1)
    
    print(f"讀取逐字稿: {transcription_path}")
    print(f"使用模型: {model_choice}")
    
    try:
        # 讀取逐字稿內容
        with open(transcription_path, 'r', encoding='utf-8') as f:
            transcription_text = f.read()
        
        # 建立筆記生成器
        notes_generator = NotesGenerator(model_choice=model_choice)
        
        # 生成筆記
        notes = notes_generator.generate_notes({"text": transcription_text})
        
        if notes:
            output_path = notes_generator.save_notes(notes, transcription_path)
            print(f"筆記生成完成，結果已保存到: {output_path}")
        else:
            print("筆記生成失敗")
            sys.exit(1)
            
    except Exception as e:
        print(f"錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
