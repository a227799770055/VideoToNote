import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import openai
import os
from openai import OpenAI
import subprocess

def download_youtube_audio(url):
    try:
        # 確保 mp3 目錄存在
        os.makedirs('mp3', exist_ok=True)
        
        command = [
            'yt-dlp',
            '--throttled-rate', '100K',  # 限制下載速度
            '-x',  
            '--audio-format', 'mp3',  
            '-o', 'mp3/%(title)s.%(ext)s',  
            '--no-warnings',
            '--quiet',
            url  
        ]
        
        print(f"正在下載: {url}")
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stderr:
            print(f"警告: {result.stderr}")
            
        print(f"下載完成: {result.stdout}")
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        error_msg = f"下載失敗: {e.stderr if e.stderr else e.stdout}"
        print(f"錯誤: {error_msg}")
        print("請確保：")
        print("1. 你已經登入 YouTube（在瀏覽器中）")
        print("2. 你的網絡連接正常")
        print("3. 影片是公開可訪問的")
        return None
    except Exception as e:
        error_msg = f"發生未預期的錯誤: {str(e)}"
        print(f"錯誤: {error_msg}")
        return None

class SpeechRecognizer:
    def __init__(self, model_id="openai/whisper-large-v3", device=None, openai_api_key=None, deepseek_api_key=None):
        self.device = device if device else ("cuda:0" if torch.cuda.is_available() else "cpu")
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, 
            torch_dtype=self.torch_dtype, 
            low_cpu_mem_usage=True, 
            use_safetensors=True
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_id)
        
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        
        if openai_api_key:
            openai.api_key = openai_api_key
            self.client=OpenAI(api_key=openai_api_key)
            self.model_flag = "openai"
        elif deepseek_api_key:
            self.client=OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
            self.model_flag = "deepseek"

    def transcribe(self, audio_path, language="chinese", return_timestamps=True):
        """
        Transcribe audio/video file to text
        
        Args:
            audio_path (str): Path to the audio/video file
            language (str): Target language for transcription
            return_timestamps (bool): Whether to include timestamps in the result
            
        Returns:
            dict: Transcription result
        """
        return self.pipe(
            audio_path,
            return_timestamps=return_timestamps,
            generate_kwargs={"language": language}
        )

    def save_transcription(self, result, audio_path):
        """
        Save transcription result to a file with the same name as the audio file
        
        Args:
            result (dict): Transcription result to save
            audio_path (str): Path to the audio file
        """
        # Get the base name of the audio file (without extension)
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = f"逐字稿/{base_name}_transcription.txt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(result))
        return output_path

    def generate_notes(self, transcription, prompt="這是一場演講的逐字稿，請你幫我整理成6000字的筆記"):
        """
        Generate notes from transcription using OpenAI API
        
        Args:
            transcription (dict): Transcription result
            prompt (str): Prompt for OpenAI API
            
        Returns:
            str: Generated notes
        """
        # Extract text from transcription result
        text = transcription['text']
        try:
            if self.model_flag == "openai":
                # Call OpenAI API using the correct format
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "你是一個專業的筆記整理專家"},
                        {"role": "user", "content": f"{prompt}\n\n逐字稿內容:\n{text}"}
                    ]
                )
            elif self.model_flag == "deepseek":
                # Call DeepSeek API using the correct format
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一個專業的筆記整理專家"},
                        {"role": "user", "content": f"{prompt}\n\n逐字稿內容:\n{text}"}
                    ]
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return ""  # Return empty string instead of None

    def save_notes(self, notes, audio_path):
        """
        Save generated notes to a file with the same name as the audio file
        
        Args:
            notes (str): Generated notes to save
            audio_path (str): Path to the audio file
        """
        # Get the base name of the audio file (without extension)
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = f"筆記/{base_name}_notes.txt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(notes if notes else "")
        return output_path

# Example usage
if __name__ == "__main__":
    recognizer = SpeechRecognizer(
        deepseek_api_key = "sk-2a313bd567344d8d9129f9f29fbb1e7d"
    )
    
    videos = ['https://youtu.be/Gx9VlRGUUeM','https://youtu.be/poFPv2DH3Xg']
    
    for video in videos:
        print(f"\n處理影片: {video}")
        download_result = download_youtube_audio(video)
        if not download_result:
            print("下載失敗，跳過此影片")
            continue
        
        try:
            destination = download_result.split('Destination: ')[-1].split('\n')[0]
            audio_path = destination.replace('.webm', '.mp3')
            
            print("開始語音辨識...")
            result = recognizer.transcribe(
                audio_path,
                language="chinese"
            )
            
            # 保存原始轉錄結果
            if result:
                transcription_path = recognizer.save_transcription(result, audio_path)
                print(f"轉錄結果已保存到: {transcription_path}")
                
                # 生成筆記
                print("生成筆記中...")
                notes = recognizer.generate_notes(result)
                
                # 保存筆記
                if notes:
                    notes_path = recognizer.save_notes(notes, audio_path)
                    print(f"筆記已保存到: {notes_path}")
                else:
                    print("生成筆記失敗")
            
            # 刪除臨時音頻文件
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    print(f"已刪除臨時文件: {audio_path}")
            except Exception as e:
                print(f"刪除臨時文件時出錯: {e}")
                
        except Exception as e:
            print(f"處理影片時出錯: {e}")
            continue
    
    print("\n所有處理完成！")