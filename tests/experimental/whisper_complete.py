import os
from pywhispercpp.model import Model

def transcribe_audio_with_whisper(audio_file, output_dir="data/transcriptions", language="zh"):
    """
    使用 pywhispercpp 進行語音辨識
    
    Args:
        audio_file: 音檔路徑
        output_dir: 輸出目錄
        language: 語言代碼 (zh=中文, en=英文, auto=自動偵測)
    """
    
    print("正在載入 Whisper 模型...")
    model = Model("small")  # 可選: "tiny", "base", "small", "medium", "large"
    
    print(f"開始辨識音檔: {audio_file}")
    print("這可能需要幾分鐘...")
    
    # 進行語音辨識
    if language == "auto":
        segments = model.transcribe(audio_file)
    else:
        segments = model.transcribe(audio_file, language=language)
    
    # 整理辨識結果
    full_transcript = ""
    segment_details = []
    
    for i, segment in enumerate(segments):
        text = segment.text.strip()
        if text:  # 忽略空白段落
            start_time = getattr(segment, 'start', i * 30)  # 估算時間（如果沒有時間戳）
            end_time = getattr(segment, 'end', (i + 1) * 30)
            
            segment_info = {
                'id': i + 1,
                'start': start_time,
                'end': end_time,
                'text': text
            }
            segment_details.append(segment_info)
            full_transcript += text + "\n\n"
    
    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 儲存完整轉錄結果
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}_whisper.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== Whisper 語音辨識結果 ===\n\n")
        f.write(f"音檔: {audio_file}\n")
        f.write(f"語言: {language}\n")
        f.write(f"總段落數: {len(segment_details)}\n")
        f.write("="*50 + "\n\n")
        
        # 寫入分段結果
        for segment in segment_details:
            f.write(f"[{segment['id']:03d}] {segment['start']:.1f}s - {segment['end']:.1f}s\n")
            f.write(f"{segment['text']}\n\n")
        
        f.write("="*50 + "\n")
        f.write("完整轉錄文本:\n\n")
        f.write(full_transcript)
    
    print(f"\n✅ 辨識完成！")
    print(f"📄 結果已儲存到: {output_file}")
    print(f"📊 總段落數: {len(segment_details)}")
    
    # 顯示前幾段預覽
    print("\n📝 辨識結果預覽:")
    print("-" * 40)
    for segment in segment_details[:3]:  # 顯示前3段
        print(f"[{segment['id']:03d}] {segment['text'][:100]}...")
    
    if len(segment_details) > 3:
        print(f"... 還有 {len(segment_details) - 3} 段")
    
    return output_file, segment_details

if __name__ == "__main__":
    # 設定音檔路徑
    audio_file = "/Users/kuangtinghsiao/workspace/videoToNote/data/mp3/Why Does Diffusion Work Better than Auto-Regression？.mp3"
    
    # 執行辨識
    output_file, segments = transcribe_audio_with_whisper(
        audio_file=audio_file,
        language="auto"  # 自動偵測語言
    )
