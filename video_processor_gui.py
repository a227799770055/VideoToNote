from flask import Flask, render_template, request, jsonify
from processor import VideoProcessor
import os
import threading
import uuid
from datetime import datetime

app = Flask(__name__)


def process_video_helper(url, request_id, model_choice=None):
    """處理影片的輔助函數"""
    # Determine model choice: use parameter or environment variable
    model_choice = model_choice or os.environ.get('MODEL_CHOICE', 'ollama')
    api_key = os.environ.get('OPENAI_API_KEY') if model_choice == 'openai' else os.environ.get('DEEPSEEK_API_KEY') if model_choice == 'deepseek' else os.environ.get('GEMINI_API_KEY')
    
    # 根據 model_choice 決定是否需要 API 金鑰
    if model_choice in ['openai', 'deepseek', 'gemini'] and not api_key:
        return {'error': f'請設定 {model_choice.upper()}_API_KEY 環境變數'}
    try:
        print(f"開始處理影片: {url}")
        processor = VideoProcessor(model_choice=model_choice, api_key=api_key)

        # 先測試下載器
        print("測試 YouTube 下載...")
        # 下載音檔
        audio_path = processor.downloader.download_audio(url)
        if not audio_path:
            return {'error': '影片下載失敗，請檢查：1) 影片是否為私人或地區限制 2) yt-dlp 是否為最新版本 3) 網路連線是否正常'}
        
        print(f"下載成功: {audio_path}")
        
        # 進行轉錄
        print("開始轉錄...")
        transcription = processor.transcriber.transcribe(audio_path)
        if not transcription:
            return {'error': '語音轉錄失敗'}
        
        # 保存轉錄結果
        transcript_path = processor.transcriber.save_transcription(transcription, audio_path)
        print(f"轉錄完成: {transcript_path}")
        
        # 生成筆記
        print("開始生成筆記...")
        notes = processor.notes_generator.generate_notes(transcription)
        if not notes:
            return {'error': '筆記生成失敗，請檢查 API Key 是否有效'}
        
        # 保存筆記
        notes_path = processor.notes_generator.save_notes(notes, audio_path)
        print(f"筆記生成完成: {notes_path}")
        
        # 清理音檔
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"已清理臨時音檔: {audio_path}")
        
        # 直接返回內容，不需要再查找檔案
        transcript_text = transcription['text'] if isinstance(transcription, dict) and 'text' in transcription else str(transcription)
        
        return {
            'transcript': transcript_text,
            'notes': notes,
            'transcript_path': transcript_path,
            'notes_path': notes_path
        }
        
    except Exception as e:
        print(f"處理過程發生錯誤: {str(e)}")
        return {'error': f'處理過程發生錯誤: {str(e)}'}

@app.route('/process_url')
def process_url():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': '請輸入 YouTube 連結'}), 400
    
    # 簡單的 URL 驗證
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return jsonify({'error': '請輸入有效的 YouTube 連結'}), 400
    
    request_id = str(uuid.uuid4())
    result = process_video_helper(url, request_id)
    
    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    if not data:
        return jsonify({'error': '無效的 JSON 資料'}), 400
    
    url = data.get('url')
    model_choice = data.get('model', 'ollama')
    if not url:
        return jsonify({'error': '請輸入 YouTube 連結'}), 400

    # 簡單的 URL 驗證
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return jsonify({'error': '請輸入有效的 YouTube 連結'}), 400
    
    request_id = str(uuid.uuid4())
    result = process_video_helper(url, request_id, model_choice)
    
    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result)

if __name__ == '__main__':
    # 檢查必要的環境變數
    model_choice = os.environ.get('MODEL_CHOICE', 'ollama')
    api_key_var = f'{model_choice.upper()}_API_KEY'
    if model_choice in ['openai', 'deepseek', 'gemini'] and not os.environ.get(api_key_var):
        print(f"警告：未設定 {api_key_var} 環境變數")
    app.run(debug=True, threaded=True)