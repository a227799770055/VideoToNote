#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoToNote 主要入口點
"""
import sys
from pathlib import Path

# 將 src 目錄加入 Python 路徑
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.interfaces.cli import main as cli_main
from src.interfaces.web.app import app

def main():
    """主入口點"""
    if len(sys.argv) > 1 and sys.argv[1] == 'web':
        # 啟動 Web 介面
        print("啟動 Web 介面...")
        print("請在瀏覽器中打開 http://localhost:5001")
        app.run(debug=True, port=5001)
    else:
        # 啟動 CLI 介面
        cli_main()

if __name__ == "__main__":
    main()
