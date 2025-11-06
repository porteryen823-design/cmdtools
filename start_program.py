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
    print("資料庫工具程式 - 快速啟動")
    print("=" * 40)
    
    # 檢查虛擬環境
    venv_path = "cmdtools_env"
    if not os.path.exists(venv_path):
        print("❌ 虛擬環境不存在，請先執行:")
        print("python -m venv cmdtools_env")
        print("cmdtools_env\\Scripts\\activate")
        print("pip install PyQt5 mysql-connector-python")
        return
    
    # 檢查設定檔案
    if not os.path.exists("config.json"):
        print("❌ config.json 不存在，請確保設定檔案存在")
        return
    
    # 啟動程式
    python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        print("❌ 虛擬環境 Python 不存在")
        return
    
    print("✅ 正在啟動資料庫工具程式...")
    
    try:
        # 使用虛擬環境的 Python 執行主程式
        result = subprocess.run([python_exe, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 程式執行錯誤: {e}")
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")

if __name__ == "__main__":
    main()