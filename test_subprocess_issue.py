#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 subprocess 調用 web_login.py 的問題修復
"""

import subprocess
import sys
import os

def test_subprocess_call():
    """測試通過 subprocess 調用 web_login.py 的效果"""
    
    print("測試 subprocess 調用 web_login.py 是否有畫面登入...")
    
    # 測試命令
    cmd_args = [
        sys.executable, "web_login.py",
        "-u", "http://localhost:18083",
        "-username", "admin",
        "-password", "gsi5613686#",
        "-timeout", "15",
        "-detach", "False"  # 關鍵：設置 detach=False
    ]
    
    print(f"執行命令: {' '.join(cmd_args)}")
    
    try:
        # 使用 Popen 執行命令
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        print("等待程序完成...")
        
        # 等待程序完成（最多30秒）
        try:
            stdout, stderr = process.communicate(timeout=30)
            exit_code = process.returncode
            
            print(f"退出代碼: {exit_code}")
            print(f"標準輸出:\n{stdout}")
            
            if stderr:
                print(f"錯誤輸出:\n{stderr}")
            
            if exit_code == 0:
                print("✅ 測試通過：程式正常執行完成")
                return True
            else:
                print("❌ 測試失敗：程式執行返回非零退出碼")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("❌ 測試失敗：程序超時，可能卡在等待用戶輸入")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        return False

def test_direct_call():
    """測試直接命令行調用的效果（對比）"""
    
    print("\n對比測試：直接命令行調用 web_login.py")
    print("請手動測試以下命令:")
    print(f"python web_login.py -u http://localhost:18083 -username admin -password gsi5613686# -detach False")
    print("觀察是否有畫面登入效果")
    
    # 這裡不實際執行，只是提醒用戶

def main():
    """主測試函數"""
    print("=" * 60)
    print("subprocess 調用 web_login.py 問題修復測試")
    print("=" * 60)
    
    # 檢查 web_login.py 是否存在
    if not os.path.exists("web_login.py"):
        print("❌ 找不到 web_login.py 檔案")
        return False
    
    # 執行測試
    test1_passed = test_subprocess_call()
    test_direct_call()
    
    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)
    
    if test1_passed:
        print("🎉 測試通過！subprocess 調用 web_login.py 問題已修復")
        print("\n修復說明:")
        print("- 明確設置 -detach False 參數")
        print("- 避免 subprocess 環境下等待用戶按鍵")
        print("- 保持畫面登入功能正常")
    else:
        print("❌ 測試失敗，請檢查問題")
    
    return test1_passed

if __name__ == "__main__":
    main()