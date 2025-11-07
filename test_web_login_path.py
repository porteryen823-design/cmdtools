# -*- coding: utf-8 -*-
"""
測試 web_login 路徑檢測邏輯
"""
import os
import sys

def test_path_detection():
    """測試路徑檢測邏輯"""
    # 模擬從 cmdtools_gui.table_widget 呼叫時的 script_dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"當前目錄: {script_dir}")
    
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
        print(f"{i}. {path}")
        print(f"   存在: {exists}")
        
        if exists and not web_login_path:
            web_login_path = path
            use_exe = path.endswith('.exe')
            print(f"   -> 選用此路徑")
    
    if web_login_path:
        print(f"\n最終選用的路徑: {web_login_path}")
        print(f"使用執行檔: {use_exe}")
        
        if use_exe:
            cmd_args = [
                web_login_path,
                "-u", "https://example.com",
                "-username", "test",
                "-password", "pass",
                "-timeout", "15",
                "-detach", "False"
            ]
        else:
            cmd_args = [
                sys.executable, web_login_path,
                "-u", "https://example.com",
                "-username", "test",
                "-password", "pass",
                "-timeout", "15",
                "-detach", "False"
            ]
        
        print(f"命令列參數: {cmd_args}")
        return True
    else:
        print("\n沒有找到 web_login 程式")
        return False

if __name__ == "__main__":
    test_path_detection()