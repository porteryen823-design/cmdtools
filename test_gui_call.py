# -*- coding: utf-8 -*-
"""
直接測試 GUI 調用方式
"""
import subprocess
import os
import sys

def test_gui_call():
    """模擬 GUI 中的調用"""
    # 模擬從 cmdtools_gui.table_widget 呼叫
    try:
        import sys
        import os
        
        # 取得 web_login.exe 的路徑
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(script_dir, "..", "web_login_tool", "dist", "web_login.exe"),
            os.path.join(script_dir, "..", "web_login_tool", "web_login.exe"),
            os.path.join(script_dir, "..", "web_login.py"),
            os.path.join("web_login_tool", "dist", "web_login.exe"),
            "web_login_tool/dist/web_login.exe",
            "web_login.py"
        ]
        
        web_login_path = None
        use_exe = False
        
        for path in possible_paths:
            if os.path.exists(path):
                web_login_path = path
                use_exe = path.endswith('.exe')
                break
        
        if not web_login_path:
            print("找不到 web_login 程式")
            return
        
        # 準備命令行參數
        if use_exe:
            cmd_args = [
                web_login_path,
                "-u", "https://httpbin.org/get",
                "-username", "test",
                "-password", "pass",
                "-timeout", "5",
                "-detach", "False"
            ]
        else:
            cmd_args = [
                sys.executable, web_login_path,
                "-u", "https://httpbin.org/get",
                "-username", "test",
                "-password", "pass",
                "-timeout", "5",
                "-detach", "False"
            ]
        
        print(f"使用路徑: {web_login_path}")
        print(f"執行命令: {cmd_args}")
        
        # 執行，僅測試能否啟動
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # 等待3秒看看能否正常啟動
        try:
            stdout, stderr = process.communicate(timeout=3)
            print(f"退出碼: {process.returncode}")
            if stdout:
                print("標準輸出:")
                print(stdout[:200] + "..." if len(stdout) > 200 else stdout)
            if stderr:
                print("錯誤輸出:")
                print(stderr[:200] + "..." if len(stderr) > 200 else stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            print("程式正常啟動並運行中（在3秒超時前）")
            print("這表示執行檔工作正常！")
            
    except Exception as e:
        print(f"測試失敗: {e}")

if __name__ == "__main__":
    test_gui_call()