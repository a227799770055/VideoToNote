import time
import requests
import sys

# API 伺服器的基礎網址
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 伺服器健康檢查通過:", response.json())
            return True
        else:
            print("❌ 伺服器回傳錯誤狀態碼:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 無法連線到伺服器，請確認您已經執行了 `python main.py api`")
        return False

def submit_video_task(youtube_url: str):
    payload = {
        "youtube_url": youtube_url,
        "model": "openai",       # 換成你想用的模型，例如 gemini
        "transcriber": "fast",   # 使用快速轉錄器
        "language": "chinese",
        "keep_audio": False
    }
    
    print(f"\n🚀 準備發送轉錄請求，目標網址: {youtube_url}")
    response = requests.post(f"{BASE_URL}/video/process", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功送出任務! 任務 ID: {data['task_id']}")
        return data['task_id']
    else:
        print("❌ 送出任務失敗:", response.text)
        return None

def poll_task_status(task_id: str):
    print("\n⏳ 開始查詢任務進度...")
    
    while True:
        response = requests.get(f"{BASE_URL}/video/status/{task_id}")
        if response.status_code != 200:
            print("❌ 查詢狀態時發生錯誤:", response.text)
            break
            
        data = response.json()
        status = data["status"]
        
        if status == "completed":
            print("\n🎉 轉錄完成！")
            print("檔案存放位置:")
            print(data.get("result", {}))
            break
        elif status == "failed":
            print("\n❌ 轉錄失敗:")
            print(data.get("error", "未知錯誤"))
            break
        elif status == "pending":
            print("🔸 任務還在排隊中 (pending)...")
        elif status == "processing":
            print("🔹 系統正在努力轉錄中 (processing)...")
            
        # 等待 5 秒後再問一次
        time.sleep(5)

def main():
    print("--- VideoToNote API 測試用戶端 ---")
    
    # 1. 檢查伺服器狀態
    if not test_health():
        sys.exit(1)
        
    # 2. 準備測試用的影片網址 (這裡使用較短的測試影片)
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # Me at the zoo (第一支 YT 影片)
    
    # 3. 送出任務取得 task_id
    task_id = submit_video_task(test_url)
    
    # 4. 如果成功取得 task_id，就開始追蹤進度
    if task_id:
        poll_task_status(task_id)

if __name__ == "__main__":
    main()
