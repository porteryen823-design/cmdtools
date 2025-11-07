# -*- coding: utf-8 -*-
"""
測試新的調用方式
"""
import subprocess
import os

def test_new_approach():
    """測試新的調用方式"""
    try:
        # 使用絕對路徑執行 web_login.exe
        exe_path = os.path.abspath("web_login_tool/dist/web_login.exe")
        print(f"執行檔路徑: {exe_path}")
        print(f"路徑存在: {os.path.exists(exe_path)}")
        
        if not os.path.exists(exe_path):
            print("❌ 執行檔不存在")
            return
        
        # 準備參數
        args = [
            "-u", "https://httpbin.org/get",
            "-username", "testuser",
            "-password", "testpass",
            "-timeout", "10",
            "-detach", "False"
        ]
        
        print(f"參數: {args}")
        
        # 使用 subprocess.run 執行並等待完成
        print("執行中...")
        result = subprocess.run([exe_path] + args, capture_output=True, text=True, timeout=15)
        
        print(f"退出碼: {result.returncode}")
        print(f"標準輸出: {result.stdout[:300]}..." if len(result.stdout) > 300 else f"標準輸出: {result.stdout}")
        print(f"錯誤輸出: {result.stderr[:300]}..." if len(result.stderr) > 300 else f"錯誤輸出: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ 執行成功！")
        else:
            print(f"❌ 執行失敗，退出碼: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("⏰ 執行超時")
    except Exception as e:
        print(f"❌ 執行異常: {e}")

if __name__ == "__main__":
    test_new_approach()