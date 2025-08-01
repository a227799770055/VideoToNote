"""
命令列介面
"""
import argparse
import sys
from processor import VideoProcessor
from config import config

def main():
    parser = argparse.ArgumentParser(description='影片/音檔轉錄與筆記生成工具')
    
    # 輸入來源
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--youtube', '-y', type=str, help='YouTube 影片連結')
    group.add_argument('--audio', '-a', type=str, help='本地音檔路徑')
    group.add_argument('--batch', '-b', type=str, nargs='+', help='批次處理多個 YouTube 連結')
    
    # API Key 選擇
    api_group = parser.add_mutually_exclusive_group()
    api_group.add_argument('--openai-key', type=str, help='OpenAI API Key')
    api_group.add_argument('--deepseek-key', type=str, help='DeepSeek API Key')
    
    # 其他選項
    parser.add_argument('--keep-audio', action='store_true', help='保留下載的音檔')
    parser.add_argument('--language', type=str, default=config.DEFAULT_LANGUAGE, 
                       help='轉錄語言（預設：chinese）')
    
    args = parser.parse_args()
    
    # 檢查 API Key
    if not args.openai_key and not args.deepseek_key and not config.OPENAI_API_KEY and not config.DEEPSEEK_API_KEY:
        print("錯誤：需要提供 OpenAI 或 DeepSeek 的 API Key")
        print("可以透過：")
        print("1. 命令列參數：--openai-key 或 --deepseek-key")
        print("2. 環境變數：OPENAI_API_KEY 或 DEEPSEEK_API_KEY")
        sys.exit(1)
    
    # 初始化處理器
    processor = VideoProcessor(
        openai_api_key=args.openai_key,
        deepseek_api_key=args.deepseek_key
    )
    
    # 執行對應的處理
    try:
        if args.youtube:
            success = processor.process_youtube_video(args.youtube, args.keep_audio)
            sys.exit(0 if success else 1)
            
        elif args.audio:
            success = processor.process_audio_file(args.audio)
            sys.exit(0 if success else 1)
            
        elif args.batch:
            results = processor.process_multiple_videos(args.batch, args.keep_audio)
            # 如果所有都成功則返回 0，否則返回 1
            sys.exit(0 if all(results) else 1)
            
    except KeyboardInterrupt:
        print("\n使用者中斷操作")
        sys.exit(1)
    except Exception as e:
        print(f"執行時發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
