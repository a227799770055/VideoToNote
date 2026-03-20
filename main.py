#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoToNote 主要入口點
"""
import sys
from pathlib import Path

from src.cli import main as cli_main

def main():
    """主入口點"""
    # 啟動 CLI 介面
    cli_main()

if __name__ == "__main__":
    main()
