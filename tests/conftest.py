"""
pytest 設定檔
"""
import pytest
import sys
from pathlib import Path

# 將 src 加入路徑
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
