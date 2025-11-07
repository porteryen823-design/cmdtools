# -*- coding: utf-8 -*-
"""
測試完整的 web_login 執行流程
"""
import subprocess
import os
import sys

def test_execution():
    """測試執行流程"""
    # 模擬從 cmdtools_gui 目錄呼叫時的 script_dir
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmdtools_gui")
    
    # 取得 web_login.exe 的路徑
    possible_paths = [
        os.path.join(script_dir, "..", "web_login_tool", "dist", "web_login.exe"),  # 執行檔路徑
        os.path.join(script_dir, "..", "web_login_tool", "web_login.exe"),          # 執行檔根目錄
        os.path.join(script_dir, "..", "web_login.py"),                             # Python 腳本路徑
        os.path.join("web_login_tool", "dist", "web_login.exe"),                   # 相對執行檔路徑
        "web_login_tool/dist/web_login.exe",                                       # 簡化執行檔路徑
        "web_login.py"                                                             # Python 腳本
    ]
    
    web_login_path = None
    use_exe = False
    
    # 尋找第一個存在的路徑
    for path in possible_paths:
        if os.path.exists(path):
            web_login_path = path
            use_exe = path.endswith('.exe')
            break
    
    if not web_login_path:
        print("沒有找到 web_login 程式")
        return
    
    print(f"使用路徑: {web_login_path}")
    print(f"使用執行檔: {use_exe}")
    
    # 準備測試命令
    if use_exe:
        cmd_args = [
            web_login_path,
            "-u", "https://httpbin.org/get",  # 測試網站
            "-username", "testuser",
            "-password", "testpass",
            "-timeout", "10",
            "-detach", "False"
        ]
    else:
        cmd_args = [
            sys.executable, web_login_path,
            "-u", "https://httpbin.org/get",
            "-username", "testuser",
            "-password", "testpass",
            "-timeout", "10",
            "-detach", "False"
        ]
    
    print(f"執行命令: {' '.join(cmd_args)}")
    
    try:
        # 執行命令
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # 等待程序完成（最多等待10秒）
        try:
            stdout, stderr = process.communicate(timeout=10)
            exit_code = process.returncode
            
            print(f"退出碼: {exit_code}")
            if stdout:
                print("標準輸出:")
                print(stdout)
            if stderr:
                print("錯誤輸出:")
                print(stderr)
            
            if exit_code == 0:
                print("✅ 執行成功！")
            else:
                print(f"❌ 執行失敗，退出碼: {exit_code}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("⏰ 程序執行超時（被終止）")
            
    except Exception as e:
        print(f"❌ 執行異常: {e}")

if __name__ == "__main__":
    test_execution()