import os
from dotenv import load_dotenv
from google.cloud import speech
import subprocess
import tempfile
import glob

# 載入 .env 文件中的環境變數
load_dotenv()

# 設置 Google Cloud 憑證路徑
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

speech_client = speech.SpeechClient()

def split_audio_file(input_file, segment_duration=60):
    """將音檔分割成較小的片段"""
    temp_dir = tempfile.mkdtemp()
    output_pattern = os.path.join(temp_dir, "segment_%03d.mp3")
    
    cmd = [
        'ffmpeg', '-i', input_file,
        '-f', 'segment',
        '-segment_time', str(segment_duration),
        '-c', 'copy',
        output_pattern
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        segments = sorted(glob.glob(os.path.join(temp_dir, "segment_*.mp3")))
        return segments, temp_dir
    except subprocess.CalledProcessError as e:
        print(f"錯誤：無法分割音檔 - {e}")
        return [], temp_dir

def transcribe_segment(segment_file):
    """辨識單個音檔片段"""
    with open(segment_file, "rb") as f:
        content = f.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        language_code="zh-TW",
        enable_automatic_punctuation=True,
    )
    
    # 對於小片段使用一般辨識
    response = speech_client.recognize(config=config, audio=audio)
    
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "
    
    return transcript.strip()

def main():
    file_name = "data/mp3/Why Does Diffusion Work Better than Auto-Regression？.mp3"
    
    print("檢查是否安裝 ffmpeg...")
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✓ ffmpeg 已安裝")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 需要安裝 ffmpeg")
        print("請執行: brew install ffmpeg")
        return
    
    print(f"分割音檔: {file_name}")
    segments, temp_dir = split_audio_file(file_name, segment_duration=50)
    
    if not segments:
        print("無法分割音檔")
        return
    
    print(f"已分割成 {len(segments)} 個片段")
    
    full_transcript = ""
    
    for i, segment in enumerate(segments):
        print(f"正在辨識片段 {i+1}/{len(segments)}...")
        try:
            transcript = transcribe_segment(segment)
            if transcript:
                full_transcript += transcript + "\n\n"
                print(f"片段 {i+1} 完成: {transcript[:100]}...")
        except Exception as e:
            print(f"片段 {i+1} 辨識失敗: {e}")
    
    # 清理臨時檔案
    import shutil
    shutil.rmtree(temp_dir)
    
    print("\n" + "="*50)
    print("完整辨識結果:")
    print("="*50)
    print(full_transcript)
    
    # 儲存結果
    output_file = "data/transcriptions/stt_result.txt"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_transcript)
    print(f"\n結果已儲存到: {output_file}")

if __name__ == "__main__":
    main()
