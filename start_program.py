#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速啟動腳本
在虛擬環境中啟動資料庫工具程式
"""

import os
import sys
import subprocess

def main():
    """啟動程式"""
    print("Database Tool - Quick Start")
    print("=" * 40)
    
    # 檢查虛擬環境
    venv_path = "cmdtools_env"
    if not os.path.exists(venv_path):
        print("❌ Virtual environment does not exist, please run:")
        print("python -m venv cmdtools_env")
        print("cmdtools_env\\Scripts\\activate")
        print("pip install PyQt5 mysql-connector-python")
        return
    
    # 檢查設定檔案
    if not os.path.exists("config.json"):
        print("❌ config.json does not exist, please ensure the configuration file exists")
        return
    
    # 啟動程式
    python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        print("❌ Virtual environment Python does not exist")
        return
    
    print("✅ Starting the Database Tool...")
    
    try:
        # 使用虛擬環境的 Python 執行主程式
        result = subprocess.run([python_exe, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Program execution error: {e}")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"❌ Startup failed: {e}")

if __name__ == "__main__":
    main()