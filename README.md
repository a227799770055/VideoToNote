# 🎬 VideoToNote (CLI 版)

**智能影片轉錄與筆記生成工具**

將 YouTube 影片或本地音檔智能轉換為結構化筆記的純指令列 (CLI) 解決方案。經過輕量化重構，移除了多餘的前端與 GUI 依賴，專注於提供高效能的核心語音轉錄與多模型 AI 筆記生成，非常適合自動化腳本或批次處理。

---

## 🌟 核心特色

- **多模態輸入**: 支援 YouTube URL 直接下載，或讀取本地音檔 (MP3, WAV, M4A 等)。
- **🚀 雙轉錄引擎**: 
  - **快速模式** (`pywhispercpp`): 支援硬體加速 (Metal, CUDA)，轉錄速度極快。
  - **標準模式** (`transformers`): 高精度，提供穩定識別。
- **📝 多模型 AI 筆記生成**: 內建策略模式，支援快速切換 OpenAI、DeepSeek、Google Gemini 及本地端 Ollama 模型。
- **極簡模組架構**: 純淨的命令列工具，以工廠模式 (Factory) 與依賴注入 (DI) 重構，具備極佳的擴展性。

---

## 🏗️ 專案架構

```
videoToNote/
├── 🚀 main.py                # 唯一主程式進入點
├── 📁 src/                   # 核心業務邏輯
│   ├── cli.py                # 終端機參數解析與調用介面
│   ├── core/                 # 核心處理器 (VideoProcessor) 與全域設定檔 
│   ├── services/             # 抽象化服務 (Transcriber, NotesGenerator, Downloader)
│   └── utils/                # 工具函式
├── 📊 data/                  # 產出的資料夾 (包含 mp3, transcriptions, notes, configs)
├── 🧪 tests/                 # 單元測試與實驗腳本
├── 📜 scripts/               # 其他獨立腳本
└── 📦 requirements/          # 專案依賴套件清單 (base, dev, prod)
```

---

## ⚡ 快速開始

### 環境準備

您可以使用 `venv` 或 `conda` 來建立獨立的虛擬環境：

**選項一：使用 venv (Python 內建)**
```bash
# 建立並啟用環境
python -m venv venv
source venv/bin/activate  # macOS / Linux
# Windows 請使用: venv\Scripts\activate
```

**選項二：使用 Conda**
```bash
# 建立並啟用環境
conda create -n ai-agent python=3.11
conda activate ai-agent
```

### 安裝專案

本專案使用現代化的 `pyproject.toml` 管理相依套件，請直接透過 `pip` 進行安裝：

```bash
# 安裝核心套件與全域指令 (video-to-note)
pip install .

# 若您需要進行開發或測試，可加上 dev 依賴
# pip install -e '.[dev]'

# (可選) 安裝快速轉錄引擎 - 強烈建議安裝以獲得 3-5 倍的速度提升
pip install pywhispercpp

# 系統依賴: 下載 YouTube 影片與音檔處理的必備工具 (yt-dlp, ffmpeg)
# macOS: brew install yt-dlp ffmpeg
# Ubuntu: sudo apt install  yt-dlp ffmpeg
```

### 配置 API 金鑰

請從設定檔範本複製一份，並填入您要使用的 AI 模型 API 金鑰：

```bash
cp config/model.yaml.example config/model.yaml
# 編輯 config/model.yaml，在 api_keys 區塊填寫對應的金鑰 (如 openai, deepseek, gemini)
```

---

## 📖 使用指南

在您的 conda 環境下，直接透過終端機執行 `main.py` 即可。

### 基本指令

```bash
# 處理 YouTube 影片 (預設自動使用 pywhispercpp 快速轉錄器與 OpenAI 模型)
python main.py --youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 處理本地端的音檔
python main.py --audio "path/to/your/audio.mp3"

# 批次處理多個影片
python main.py --batch "影片網址1" "影片網址2"
```

### 進階參數設定

- **選擇 AI 模型 (`--model`)**: 支援 `openai` (預設), `deepseek`, `gemini`, `ollama`。
- **選擇轉錄器 (`--transcriber`)**: 支援 `fast` (預設) 與 `standard`。
- **保留音檔 (`--keep-audio`)**: 轉錄完成後不刪除暫存音檔。
- **指定語言 (`--language`)**: 轉錄的目標語言 (預設為 `chinese`)。
- **直接傳遞 API 金鑰 (`--api-key`)**: 從終端機直接提供金鑰而不使用 `model.yaml`。

**完整參數組合範例**：
```bash
python main.py \
  --youtube "https://youtu.be/xyz" \
  --model gemini \
  --transcriber fast \
  --keep-audio \
  --language chinese
```

您隨時可以使用以下指令來查看所有可用參數：
```bash
python main.py --help
```

---

## 🎵 批次影片轉音檔 (convert2audio.py)

若您有大量本地影片需要先轉換為音訊，可使用 `scripts/convert2audio.py` 進行批次處理。此腳本會將指定資料夾中所有支援的影片格式（`.m2ts`, `.mp4`, `.mkv`, `.mov`, `.avi`, `.flv`, `.wmv`）轉換為 192kbps MP3 檔案。

> **前置需求**：系統需安裝 `ffmpeg`（`brew install ffmpeg`）。

### 基本用法

```bash
# 使用預設路徑 (輸入: ~/Downloads/video，輸出: ./data/mp3)
python scripts/convert2audio.py

# 指定輸入與輸出資料夾
python scripts/convert2audio.py -i /path/to/videos -o /path/to/output

# 強制覆蓋已存在的音檔
python scripts/convert2audio.py -i /path/to/videos -o /path/to/output -f
```

### 參數說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-i` / `--input` | 輸入影片資料夾路徑 | `~/Downloads/video` |
| `-o` / `--output` | 輸出音檔資料夾路徑 | `./data/mp3` |
| `-f` / `--force` | 強制覆蓋已存在的 MP3 檔案 | 否 |

轉換完成後，即可將輸出的 MP3 傳入主程式進行轉錄：

```bash
python main.py --audio ./data/mp3/your_file.mp3
```
