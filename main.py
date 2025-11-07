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
    print(f"匯入錯誤: {e}")
    print("請確保已安裝所需的套件:")
    print("pip install -r requirements.txt")
    sys.exit(1)

import subprocess

if __name__ == "__main__":
    try:
        # 假設你要呼叫 C:\Tools\mytool.exe，並傳入兩個參數
        #exe_path = r"C:\VSCode_Proj\myTools\web_login_tool\dist\web_login.exe"
        #args = ["-u", "http://localhost:18083", "-username","admin", "-password","gsi5613686#"]

        # 執行並等待完成
        #result = subprocess.run([exe_path] + args, capture_output=True, text=True)

        #print("標準輸出:", result.stdout)
        #print("錯誤輸出:", result.stderr)

        main()
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
        sys.exit(0)
    except Exception as e:
        print(f"程式執行時發生未預期的錯誤: {e}")
        sys.exit(1)