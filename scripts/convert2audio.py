import os
import subprocess
import argparse
import shutil
from pathlib import Path

def batch_convert_to_mp3(input_folder, output_folder, overwrite=False):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # 檢查輸入資料夾是否存在
    if not input_path.exists() or not input_path.is_dir():
        print(f"錯誤: 找不到輸入資料夾 ({input_folder})")
        return

    # 檢查 FFmpeg 是否安裝
    if not shutil.which('ffmpeg'):
        print("錯誤: 找不到 ffmpeg 指令，請確保已安裝並加入到系統環境變數中。")
        return

    # 支援的影片副檔名清單
    video_extensions = {'.m2ts', '.mp4', '.mkv', '.mov', '.avi', '.flv', '.wmv'}
    
    # 若輸出資料夾不存在則建立
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"輸出資料夾: {output_path}")

    # 遍歷資料夾中的所有檔案
    for file_path in input_path.iterdir():
        # 確保是檔案且副檔名符合
        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
            # 決定輸出的檔案路徑 (.mp3)
            out_file = output_path / f"{file_path.stem}.mp3"

            # 避免重複轉檔：如果檔案已存在且不強制覆蓋，就跳過
            if out_file.exists() and not overwrite:
                print(f"略過: {file_path.name} (已存在)")
                continue

            print(f"正在處理: {file_path.name}...")

            command = [
                'ffmpeg',
                '-i', str(file_path),
                '-vn',
                '-c:a', 'libmp3lame',
                '-b:a', '192k',
                '-y' if overwrite else '-n', # -y: 覆蓋, -n: 不覆蓋
                str(out_file)
            ]

            try:
                # capture_output=True 可以捕捉輸出而不直接印在終端機
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                print(f"完成: {out_file.name}")
            except subprocess.CalledProcessError as e:
                print(f"失敗: 無法轉換 {file_path.name}")
                print(f"詳細錯誤訊息: \n{e.stderr}")

    print("\n--- 所有任務處理完畢 ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="批次將影片轉換為 mp3 音檔")
    parser.add_argument("-i", "--input", default="/Users/kuangtinghsiao/Downloads/video", help="輸入影片資料夾路徑 (預設: ./my_videos)")
    parser.add_argument("-o", "--output", default="./data/mp3", help="輸出音檔資料夾路徑 (預設: ./data/mp3)")
    parser.add_argument("-f", "--force", action="store_true", help="如果音檔已存在，強制覆蓋轉檔")
    
    args = parser.parse_args()
    
    batch_convert_to_mp3(args.input, args.output, overwrite=args.force)