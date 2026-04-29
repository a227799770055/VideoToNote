#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoToNote 主要入口點
"""
import sys
from pathlib import Path
import uvicorn

from src.cli import main as cli_main

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        print("🚀 啟動 VideoToNote API 伺服器...")
        # 移除 'api' 參數，避免影響後續的 argparse 等
        sys.argv.pop(1)
        uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        # 啟動 CLI 介面
        cli_main()

if __name__ == "__main__":
    main()
