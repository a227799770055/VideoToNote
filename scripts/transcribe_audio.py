#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
獨立轉錄腳本 - 僅轉錄音檔，不生成筆記
"""
import sys
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.transcriber import SpeechTranscriber
from src.core.config import config

def main():
    if len(sys.argv) < 2:
        print("用法: python transcribe_audio.py <音檔路徑>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    if not Path(audio_path).exists():
        print(f"錯誤: 音檔不存在 - {audio_path}")
        sys.exit(1)
    
    print(f"開始轉錄音檔: {audio_path}")
    
    try:
        transcriber = SpeechTranscriber()
        result = transcriber.transcribe(audio_path)
        
        if result:
            output_path = transcriber.save_transcription(result, audio_path)
            print(f"轉錄完成，結果已保存到: {output_path}")
        else:
            print("轉錄失敗")
            sys.exit(1)
            
    except Exception as e:
        print(f"錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
