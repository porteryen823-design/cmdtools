#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫工具程式 - 主程式入口
命令工具和提示工具管理系統
"""

import sys
import os

# 將當前目錄加入 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from cmdtools_gui.main_window import main
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure the required packages are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

import subprocess

if __name__ == "__main__":
    try:
        # ... existing code ...

        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred during program execution: {e}")
        sys.exit(1)