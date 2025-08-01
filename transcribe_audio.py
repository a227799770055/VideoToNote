import sys
from app import SpeechRecognizer

def transcribe_audio(audio_path, openai_api_key=None, deepseek_api_key=None):
    try:
        if openai_api_key:
            recognizer = SpeechRecognizer(openai_api_key=openai_api_key)
        elif deepseek_api_key:
            recognizer = SpeechRecognizer(deepseek_api_key=deepseek_api_key)
        else:
            print("請提供 API Key")
            return

        print("開始語音辨識...")
        result = recognizer.transcribe(audio_path, language="chinese")
        import sys
import os
from processor import VideoProcessor

def transcribe_audio(audio_path, openai_api_key=None, deepseek_api_key=None):
    try:
        processor = VideoProcessor(
            openai_api_key=openai_api_key,
            deepseek_api_key=deepseek_api_key
        )

        print("開始語音辨識...")
        transcription = processor.transcriber.transcribe(audio_path, language="chinese")
        
        if transcription:
            # 顯示轉錄結果
            text = transcription['text'] if isinstance(transcription, dict) and 'text' in transcription else str(transcription)
            print("辨識完成，逐字稿如下：\n")
            print(text)

            # 儲存成 txt 檔案
            transcription_path = processor.transcriber.save_transcription(transcription, audio_path)
            print(f"逐字稿已儲存到: {transcription_path}")
        else:
            print("轉錄失敗")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python transcribe_audio.py <音檔路徑>")
        sys.exit(1)

    audio_path = sys.argv[1]
    # 這裡請自行填入你的 API Key
    openai_api_key = None
    deepseek_api_key = "sk-2a313bd567344d8d9129f9f29fbb1e7d"

    transcribe_audio(audio_path, deepseek_api_key=deepseek_api_key)