# -*- coding: utf-8 -*-
"""
Flask Web 應用
"""
from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
from ...core.processor import VideoProcessor, FastVideoProcessor
from ...core.config import config

# Flask 應用初始化
app = Flask(__name__)

# 確保 templates 目錄使用正確路徑
template_dir = Path(__file__).parent / "templates"
app.template_folder = str(template_dir)

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    """處理影片請求"""
    try:
        data = request.get_json()
        url = data.get('url')
        model = data.get('model', 'openai')
        transcriber = data.get('transcriber', 'fast')  # 預設使用快速轉錄器
        keep_audio = data.get('keep_audio', False)
        
        if not url:
            return jsonify({'success': False, 'error': '請提供 YouTube 連結'})
        
        # 建立處理器 - 根據選擇使用不同的轉錄器
        if transcriber == 'fast':
            print("使用快速轉錄器 (pywhispercpp)!!!!!")
            processor = FastVideoProcessor(model_choice=model)
        else:
            processor = VideoProcessor(model_choice=model, transcriber_type='standard')
        
        # 處理影片
        success = processor.process_youtube_video(url, keep_audio)
        
        if success:
            return jsonify({'success': True, 'message': '處理完成！'})
        else:
            return jsonify({'success': False, 'error': '處理失敗'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """處理音檔請求"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': '請選擇音檔'})
        
        file = request.files['audio']
        model = request.form.get('model', 'openai')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': '請選擇音檔'})
        
        # 保存上傳的檔案
        filename = file.filename
        audio_path = config.MP3_DIR / filename
        file.save(str(audio_path))
        
        # 建立處理器 - 預設使用快速轉錄器
        processor = VideoProcessor(model_choice=model)  # 現在預設就是 fast
        
        # 處理音檔
        success = processor.process_audio_file(str(audio_path))
        
        if success:
            return jsonify({'success': True, 'message': '處理完成！'})
        else:
            return jsonify({'success': False, 'error': '處理失敗'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
