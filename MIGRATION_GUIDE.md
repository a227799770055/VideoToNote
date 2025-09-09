# VideoToNote 重構遷移指南

## 重構完成狀態

✅ **重構已成功完成！** 所有基本功能測試通過。

## 新的目錄結構

```
videoToNote/
├── src/                          # 主要原始碼
│   ├── __init__.py
│   ├── core/                     # 核心業務邏輯
│   │   ├── __init__.py
│   │   ├── config.py             # 設定管理
│   │   └── processor.py          # 主處理器
│   ├── services/                 # 服務層
│   │   ├── __init__.py
│   │   ├── downloader.py         # YouTube下載服務
│   │   ├── transcriber.py        # 轉錄服務
│   │   └── notes_generator.py    # 筆記生成服務
│   ├── interfaces/               # 使用者介面
│   │   ├── __init__.py
│   │   ├── cli.py               # 命令列介面
│   │   └── web/                 # Web介面
│   │       ├── __init__.py
│   │       └── app.py           # Flask應用
│   └── utils/                   # 工具函式
│       ├── __init__.py
│       └── file_manager.py      # 檔案管理工具
├── data/                        # 資料目錄（新）
│   ├── mp3/                     # 音檔目錄
│   ├── transcriptions/          # 轉錄檔案目錄
│   └── notes/                   # 筆記檔案目錄
├── scripts/                     # 獨立腳本
├── tests/                       # 測試程式碼
├── requirements/                # 依賴管理
├── main.py                      # 主要入口點
└── setup.py                     # 套件安裝設定
```

## 使用方式

### CLI 模式 (命令列)
```bash
# 基本使用
conda activate video2note
python main.py --youtube "https://youtube.com/watch?v=..." --model ollama

# 處理本地音檔
python main.py --audio "data/mp3/your_file.mp3" --model openai

# 批次處理
python main.py --batch "url1" "url2" "url3" --model deepseek
```

### Web 模式
```bash
conda activate video2note
python main.py web
# 然後在瀏覽器打開 http://localhost:5001
```

## 向後兼容性

- ✅ 舊的根目錄檔案（如 `processor.py`, `config.py`）仍然可用
- ✅ 舊的 `mp3/`, `逐字稿/`, `筆記/` 目錄繼續支援
- ✅ 所有原有的 CLI 參數和功能保持不變

## 新功能

1. **更好的模組化結構**：代碼按功能分層組織
2. **統一的配置管理**：所有設定集中在 `src/core/config.py`
3. **改進的檔案管理**：使用 pathlib 進行路徑處理
4. **標準化的目錄結構**：符合 Python 專案最佳實踐
5. **更好的測試支援**：獨立的測試目錄和框架

## 資料遷移建議

如果你想完全使用新的目錄結構，可以執行：

```bash
# 遷移音檔
cp mp3/* data/mp3/

# 遷移轉錄檔案
cp 逐字稿/* data/transcriptions/

# 遷移筆記
cp 筆記/* data/notes/
```

## 開發相關

### 安裝開發依賴
```bash
pip install -r requirements/dev.txt
```

### 運行測試
```bash
python -m pytest tests/
```

### 構建套件
```bash
pip install -e .
```

## 環境設定

複製並編輯環境變數檔案：
```bash
cp .env.example .env
# 然後編輯 .env 檔案，加入你的 API keys
```

## 故障排除

### Web 介面端口衝突
如果端口 5001 被佔用，可以修改 `main.py` 中的端口號碼。

### 模組導入問題
確保在專案根目錄運行命令，或使用 `pip install -e .` 安裝開發版本。

### 權限問題
確保 `data/` 目錄有適當的讀寫權限。

---

重構已完成！🎉 
系統保持完整的向後兼容性，你可以繼續使用原有的方式，也可以逐步遷移到新的目錄結構。
