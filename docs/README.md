# VideoToNote

一個功能豐富的 YouTube 影片轉錄與筆記生成工具，支援多種 AI 模型，提供 CLI 和 Web 兩種使用介面。

## 🚀 功能特色

- **YouTube 影片下載**: 自動下載 YouTube 影片音檔
- **語音轉錄**: 使用 OpenAI Whisper 模型進行高精度語音轉文字
- **智能筆記生成**: 支援多種 AI 模型生成結構化筆記
- **多種使用方式**: 命令列工具和 Web 介面
- **批次處理**: 支援同時處理多個影片
- **模組化架構**: 清晰的程式碼結構，易於維護和擴展

## 📋 支援的 AI 模型

- **OpenAI GPT-4o-mini**: 高品質的筆記生成
- **DeepSeek**: 性價比優秀的國產模型
- **Google Gemini**: Google 的先進 AI 模型  
- **Ollama**: 本地運行的開源模型

## 🛠️ 安裝

### 1. 克隆專案

```bash
git clone https://github.com/yourusername/VideoToNote.git
cd VideoToNote
```

### 2. 安裝依賴

```bash
# 基本依賴
pip install -r requirements/base.txt

# 開發依賴 (如果需要)
pip install -r requirements/dev.txt

# 生產環境依賴 (如果部署)
pip install -r requirements/prod.txt
```

### 3. 設定環境變數

複製環境變數範本並填入您的 API 金鑰：

```bash
cp .env.example .env
# 編輯 .env 檔案，填入您的 API 金鑰
```

### 4. 安裝系統依賴

確保您的系統已安裝 `yt-dlp`:

```bash
# macOS
brew install yt-dlp

# Ubuntu/Debian  
sudo apt install yt-dlp

# 或使用 pip
pip install yt-dlp
```

## 📖 使用方式

### 命令列介面 (CLI)

#### 處理 YouTube 影片

```bash
# 基本使用
python main.py --youtube "https://www.youtube.com/watch?v=..."

# 指定模型
python main.py --youtube "https://www.youtube.com/watch?v=..." --model deepseek

# 保留音檔
python main.py --youtube "https://www.youtube.com/watch?v=..." --keep-audio

# 批次處理
python main.py --batch "url1" "url2" "url3"
```

#### 處理本地音檔

```bash
python main.py --audio "/path/to/your/audio.mp3"
```

### Web 介面

啟動 Web 服務：

```bash
python main.py web
```

然後在瀏覽器中開啟 `http://localhost:5000`

### 獨立腳本

#### 僅轉錄音檔

```bash
python scripts/transcribe_audio.py "/path/to/audio.mp3"
```

#### 從逐字稿生成筆記

```bash
python scripts/generate_note.py "/path/to/transcription.txt" openai
```

## 📁 專案結構

```
videoToNote/
├── src/                          # 主要原始碼
│   ├── core/                     # 核心業務邏輯
│   │   ├── config.py             # 設定管理
│   │   └── processor.py          # 主處理器
│   ├── services/                 # 服務層
│   │   ├── downloader.py         # YouTube下載服務
│   │   ├── transcriber.py        # 轉錄服務
│   │   └── notes_generator.py    # 筆記生成服務
│   ├── interfaces/               # 使用者介面
│   │   ├── cli.py               # 命令列介面
│   │   └── web/                 # Web介面
│   │       ├── app.py           # Flask應用
│   │       └── templates/
│   │           └── index.html
│   └── utils/                   # 工具函式
│       └── file_manager.py      # 檔案管理工具
├── data/                        # 資料目錄
│   ├── mp3/                     # 音檔
│   ├── transcriptions/          # 逐字稿
│   └── notes/                   # 筆記
├── tests/                       # 測試程式碼
├── scripts/                     # 獨立腳本
├── requirements/                # 依賴管理
└── main.py                      # 主要入口點
```

## ⚙️ 設定

### 環境變數

在 `.env` 檔案中設定您的 API 金鑰：

```env
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here  
GEMINI_API_KEY=your_gemini_api_key_here
```

### 模型設定

您可以在 `src/core/config.py` 中調整各種設定：

- API 端點
- 模型名稱
- 預設提示詞
- 檔案路徑

## 🧪 測試

運行測試：

```bash
# 運行所有測試
python -m unittest discover tests

# 運行特定測試
python -m unittest tests.test_processor
```

## 📦 部署

### 本地部署

```bash
# 使用 gunicorn 運行 Web 服務
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.interfaces.web.app:app"
```

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements/prod.txt

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.interfaces.web.app:app"]
```

## 🤝 貢獻

歡迎提交 Issues 和 Pull Requests！

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權

此專案使用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙋‍♂️ 支援

如果您遇到問題或有任何疑問：

- 提交 [Issue](https://github.com/yourusername/VideoToNote/issues)
- 發送郵件至：your.email@example.com

## 🙏 致謝

- [OpenAI Whisper](https://github.com/openai/whisper) - 語音轉錄
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 下載
- [Transformers](https://huggingface.co/transformers/) - 機器學習模型
- [Flask](https://flask.palletsprojects.com/) - Web 框架
