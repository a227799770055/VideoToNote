# -*- coding: utf-8 -*-
"""
命令列介面
"""
import argparse
import sys
from ..core.processor import VideoProcessor, FastVideoProcessor
from ..core.config import config

def main():
    parser = argparse.ArgumentParser(description='影片/音檔轉錄與筆記生成工具')
    
    # 輸入來源
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--youtube', '-y', type=str, help='YouTube 影片連結')
    group.add_argument('--audio', '-a', type=str, help='本地音檔路徑')
    group.add_argument('--batch', '-b', type=str, nargs='+', help='批次處理多個 YouTube 連結')
    
    # API Key 選擇 (非必要，Ollama不需要)
    parser.add_argument('--api-key', type=str, help='指定要使用的 API Key')
    
    # 模型選擇
    parser.add_argument('--model', type=str, default='openai', choices=['openai', 'deepseek', 'gemini', 'ollama'],
                       help='選擇用於生成筆記的模型 (預設: openai)')
    
    # 轉錄器選擇
    parser.add_argument('--transcriber', type=str, default='fast', choices=['standard', 'fast'],
                       help='選擇轉錄器類型 (standard: transformers, fast: pywhispercpp, 預設: fast)')

    # 其他選項
    parser.add_argument('--keep-audio', action='store_true', help='保留下載的音檔')
    parser.add_argument('--language', type=str, default=config.DEFAULT_LANGUAGE, 
                       help='轉錄語言（預設：chinese）')
    
    args = parser.parse_args()
    
    try:
        # 建立處理器 - 根據選擇使用不同的轉錄器
        if args.transcriber == 'fast':
            processor = FastVideoProcessor(
                model_choice=args.model,
                api_key=args.api_key
            )
        else:
            processor = VideoProcessor(
                model_choice=args.model,
                api_key=args.api_key,
                transcriber_type='standard'
            )
        
        # 根據輸入類型處理
        if args.youtube:
            success = processor.process_youtube_video(args.youtube, args.keep_audio)
            sys.exit(0 if success else 1)
            
        elif args.audio:
            success = processor.process_audio_file(args.audio)
            sys.exit(0 if success else 1)
            
        elif args.batch:
            results = processor.process_multiple_videos(args.batch, args.keep_audio)
            # 如果有任何失敗，返回錯誤碼
            success = all(results)
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n用戶中斷操作")
        sys.exit(1)
    except Exception as e:
        print(f"程式執行錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
