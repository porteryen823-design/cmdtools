#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 web_login.py 的 detach 功能
"""

import subprocess
import sys

def test_detach_parameter():
    """測試 detach 參數是否正確添加到函數定義和命令行參數中"""
    
    print("正在測試 web_login.py 的 detach 參數功能...")
    
    # 檢查函數定義是否包含 detach 參數
    try:
        with open('web_login.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查函數簽名
        if 'def login_website(' in content and 'detach=True' in content:
            print("[OK] 函數定義包含 detach 參數")
        else:
            print("[FAIL] 函數定義缺少 detach 參數")
            return False
            
        # 檢查命令行參數
        if "parser.add_argument('-detach'" in content:
            print("[OK] 命令行參數包含 -detach")
        else:
            print("[FAIL] 命令行參數缺少 -detach")
            return False
            
        # 檢查 Chrome 選項設置
        if 'options.add_experimental_option("detach"' in content:
            print("[OK] Chrome 選項包含 detach 設置")
        else:
            print("[FAIL] Chrome 選項缺少 detach 設置")
            return False
            
        # 檢查調用是否傳遞 detach 參數
        if 'detach=args.detach' in content:
            print("[OK] 函數調用包含 detach 參數")
        else:
            print("[FAIL] 函數調用缺少 detach 參數")
            return False
        
        print("[OK] 所有 detach 參數功能檢查通過！")
        return True
        
    except Exception as e:
        print(f"[ERROR] 測試過程中發生錯誤: {e}")
        return False

def test_help_output():
    """測試命令行幫助是否顯示 detach 參數"""
    
    print("\n正在測試命令行幫助輸出...")
    
    try:
        result = subprocess.run([sys.executable, 'web_login.py', '--help'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            help_text = result.stdout
            if '-detach' in help_text and '保持瀏覽器開啟' in help_text:
                print("[OK] 命令行幫助包含 detach 參數說明")
                print(f"幫助信息: {help_text.split('-detach')[1].split('\n')[0]}")
                return True
            else:
                print("[FAIL] 命令行幫助缺少 detach 參數說明")
                print("幫助輸出:")
                print(result.stdout)
                return False
        else:
            print("[FAIL] 無法獲取幫助信息")
            return False
            
    except Exception as e:
        print(f"[ERROR] 測試幫助輸出時發生錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("=" * 60)
    print("web_login.py detach 參數功能測試")
    print("=" * 60)
    
    # 執行測試
    test1_passed = test_detach_parameter()
    test2_passed = test_help_output()
    
    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("[SUCCESS] 所有測試通過！web_login.py 已成功支援 detach 參數")
        print("\n使用方法:")
        print("  python web_login.py -u http://example.com -username test -password pass")
        print("  python web_login.py -u http://example.com -username test -password pass -detach False")
        print("  python web_login.py -u http://example.com -username test -password pass -detach True")
    else:
        print("[FAIL] 部分測試失敗，請檢查代碼實現")
    
    return test1_passed and test2_passed

if __name__ == "__main__":
    main()