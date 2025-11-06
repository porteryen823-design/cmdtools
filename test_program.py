#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程式基本功能測試腳本
檢查模組結構和基本功能
"""

import sys
import os

# 將當前目錄加入 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """測試模組導入"""
    try:
        print("=== 測試模組導入 ===")
        
        # 測試資料庫模組（使用模擬）
        from cmdtools_gui.database import DatabaseManager
        print("OK DatabaseManager 模組導入成功")
        
        # 測試對話框模組
        from cmdtools_gui.dialogs import EditRecordDialog, ExportDialog, ConfirmDialog
        print("OK 對話框模組導入成功")
        
        # 測試表格模組
        from cmdtools_gui.table_widget import FilterWidget, DataTableWidget, TableTabWidget
        print("OK 表格模組導入成功")
        
        # 測試主視窗模組
        from cmdtools_gui.main_window import MainWindow
        print("OK 主視窗模組導入成功")
        
        print("\n=== 所有模組導入成功 ===")
        return True
        
    except ImportError as e:
        print(f"FAIL 模組導入失敗: {e}")
        return False
    except Exception as e:
        print(f"ERROR 其他錯誤: {e}")
        return False

def test_config():
    """測試配置檔案"""
    try:
        print("\n=== 測試配置檔案 ===")
        
        import json
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_keys = ['DBServer', 'DBPort', 'DBUser', 'DBPassword', 'DataBase']
        for key in required_keys:
            if key in config:
                print(f"OK {key}: {config[key]}")
            else:
                print(f"FAIL 缺少配置項: {key}")
                return False
        
        return True
        
    except FileNotFoundError:
        print("FAIL config.json 檔案不存在")
        return False
    except Exception as e:
        print(f"FAIL 配置檔案錯誤: {e}")
        return False

def test_requirements():
    """測試依賴套件清單"""
    try:
        print("\n=== 測試依賴套件清單 ===")
        
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        for req in requirements:
            if req.strip():
                print(f"OK {req}")
        
        return True
        
    except FileNotFoundError:
        print("FAIL requirements.txt 檔案不存在")
        return False
    except Exception as e:
        print(f"FAIL 依賴檔案錯誤: {e}")
        return False

def test_file_structure():
    """測試檔案結構"""
    try:
        print("\n=== 測試檔案結構 ===")
        
        required_files = [
            'main.py',
            'config.json',
            'requirements.txt',
            'README.md',
            'cmdtools_gui/__init__.py',
            'cmdtools_gui/database.py',
            'cmdtools_gui/dialogs.py',
            'cmdtools_gui/table_widget.py',
            'cmdtools_gui/main_window.py'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"OK {file_path}")
            else:
                print(f"FAIL 缺少檔案: {file_path}")
                return False
        
        return True
        
    except Exception as e:
        print(f"FAIL 檔案結構檢查錯誤: {e}")
        return False

def test_syntax():
    """測試語法"""
    try:
        print("\n=== 測試語法檢查 ===")
        
        files_to_check = [
            'cmdtools_gui/database.py',
            'cmdtools_gui/dialogs.py', 
            'cmdtools_gui/table_widget.py',
            'cmdtools_gui/main_window.py',
            'main.py'
        ]
        
        import py_compile
        for file_path in files_to_check:
            if os.path.exists(file_path):
                py_compile.compile(file_path, doraise=True)
                print(f"OK 語法檢查: {file_path}")
            else:
                print(f"FAIL 檔案不存在: {file_path}")
                return False
        
        return True
        
    except Exception as e:
        print(f"FAIL 語法檢查錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("資料庫工具程式 - 基本功能測試")
    print("=" * 50)
    
    tests = [
        ("檔案結構", test_file_structure),
        ("配置檔案", test_config),
        ("依賴套件", test_requirements),
        ("語法檢查", test_syntax),
        ("模組導入", test_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\nSUCCESS {test_name} 測試通過")
            else:
                print(f"\nFAILED {test_name} 測試失敗")
        except Exception as e:
            print(f"\nERROR {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("\n恭喜！所有測試通過！程式已準備就緒。")
        print("\n下一步:")
        print("1. 安裝依賴套件: pip install -r requirements.txt")
        print("2. 設定 config.json 中的資料庫連線資訊")
        print("3. 啟動程式: python main.py")
    else:
        print("\n警告：部分測試失敗，請檢查上述錯誤。")
    
    return passed == total

if __name__ == "__main__":
    main()