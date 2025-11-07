# -*- coding: utf-8 -*-
"""
模擬從 cmdtools_gui 目錄測試路徑檢測
"""
import os
import sys

def test_gui_path():
    """模擬從 cmdtools_gui 目錄測試"""
    # 模擬 cmdtools_gui 目錄
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmdtools_gui")
    print(f"模擬 cmdtools_gui 目錄: {script_dir}")
    
    # 嘗試多個可能的路徑
    possible_paths = [
        os.path.join(script_dir, "..", "web_login_tool", "dist", "web_login.exe"),  # 執行檔路徑
        os.path.join(script_dir, "..", "web_login_tool", "web_login.exe"),          # 執行檔根目錄
        os.path.join(script_dir, "..", "web_login.py"),                             # Python 腳本路徑
        os.path.join("web_login_tool", "dist", "web_login.exe"),                   # 相對執行檔路徑
        "web_login_tool/dist/web_login.exe",                                       # 簡化執行檔路徑
        "web_login.py"                                                             # Python 腳本
    ]
    
    print("\n測試所有可能的路徑：")
    web_login_path = None
    use_exe = False
    
    for i, path in enumerate(possible_paths, 1):
        exists = os.path.exists(path)
        abs_path = os.path.abspath(path) if not os.path.isabs(path) else path
        print(f"{i}. {path}")
        print(f"   絕對路徑: {abs_path}")
        print(f"   存在: {exists}")
        
        if exists and not web_login_path:
            web_login_path = path
            use_exe = path.endswith('.exe')
            print(f"   -> 選用此路徑")
    
    if web_login_path:
        print(f"\n最終選用的路徑: {web_login_path}")
        print(f"使用執行檔: {use_exe}")
        return True
    else:
        print("\n沒有找到 web_login 程式")
        return False

if __name__ == "__main__":
    test_gui_path()