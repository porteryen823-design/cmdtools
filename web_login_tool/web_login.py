# -*- coding: utf-8 -*-
"""
Web登入程式 - 專門用於網站登入的Command Line工具
基於 test_login_improved.py 創建，專注於實際登入操作
"""

import argparse
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

def login_website(url, username, password, username_webid=None, password_webid=None,
                 headless=False, timeout=10, browser_path=None, driver_path=None, detach=True):
    """
    執行網站登入
    
    Args:
        url: 網站URL
        username: 用戶名
        password: 密碼
        username_webid: 用戶名輸入框的ID（可選）
        password_webid: 密碼輸入框的ID（可選）
        headless: 是否使用無頭模式
        timeout: 元素等待超時時間
        browser_path: 瀏覽器執行檔路徑（可選）
        driver_path: WebDriver路徑（可選）
        detach: 是否在程式結束後保持瀏覽器開啟（預設: True）
    
    Returns:
        dict: 包含登入結果和狀態的字典
    """
    driver = None
    result = {
        'success': False,
        'message': '',
        'final_url': '',
        'error': None
    }
    
    try:
        # 創建Chrome選項
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=800,600')
        
        # 設置 detach 參數
        if detach:
            options.add_experimental_option("detach", True)
        
        # 設置瀏覽器路徑（如果提供）
        if browser_path:
            options.binary_location = browser_path
        
        # 創建WebDriver
        if driver_path:
            service = Service(driver_path)
            driver = webdriver.Chrome(options=options, service=service)
        else:
            driver = webdriver.Chrome(options=options)
        
        print(f"[INFO] 正在打開網站: {url}")
        driver.get(url)
        
        # 等待頁面加載
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[type="email"]'))
            )
            print("[INFO] 網站加載完成")
        except TimeoutException:
            print("[WARN] 未找到用戶名輸入框，嘗試繼續...")
        
        # 定位用戶名輸入框
        username_input = None
        if username_webid:
            try:
                # 檢查是否包含空格，如果是則視為CSS選擇器
                if ' ' in username_webid:
                    username_input = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, username_webid))
                    )
                    print(f"[INFO] 使用CSS選擇器 '{username_webid}' 找到用戶名輸入框")
                else:
                    username_input = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.ID, username_webid))
                    )
                    print(f"[INFO] 使用ID {username_webid} 找到用戶名輸入框")
            except (TimeoutException, NoSuchElementException):
                print(f"[WARN] {username_webid} 定位失敗，嘗試其他方法...")
            except Exception as e:
                print(f"[ERROR] CSS選擇器語法錯誤: {str(e)}")
                print(f"[HINT] 常見CSS選擇器語法錯誤:")
                print(f"  - 錯誤: class=\"el-input__inner\" type=\"text\"")
                print(f"  - 正確: input.el-input__inner[type=\"text\"]")
                print(f"  - 正確: input[type=\"text\"]")
                print(f"  - 正確: .el-input__inner[type=\"text\"]")
                # 重新拋出異常以觸發其他方法
                raise
        
        if not username_input:
            selectors = [
                'input[type="text"]',
                'input[type="email"]',
                'input.el-input__inner[type="text"]',
                'input[placeholder*="用戶" i]',
                'input[placeholder*="username" i]',
                'input[placeholder*="name" i]'
            ]
            
            for selector in selectors:
                try:
                    username_input = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"[INFO] 使用選擇器 '{selector}' 找到用戶名輸入框")
                    break
                except TimeoutException:
                    continue
            
            if not username_input:
                raise Exception("無法找到用戶名輸入框")
        
        # 定位密碼輸入框
        password_input = None
        if password_webid:
            try:
                # 檢查是否包含空格，如果是則視為CSS選擇器
                if ' ' in password_webid:
                    password_input = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, password_webid))
                    )
                    print(f"[INFO] 使用CSS選擇器 '{password_webid}' 找到密碼輸入框")
                else:
                    password_input = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.ID, password_webid))
                    )
                    print(f"[INFO] 使用ID {password_webid} 找到密碼輸入框")
            except (TimeoutException, NoSuchElementException):
                print(f"[WARN] {password_webid} 定位失敗，嘗試其他方法...")
        
        if not password_input:
            selectors = [
                'input[type="password"]',
                'input.el-input__inner[type="password"]',
                'input[placeholder*="密" i]',
                'input[placeholder*="password" i]'
            ]
            
            for selector in selectors:
                try:
                    password_input = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"[INFO] 使用選擇器 '{selector}' 找到密碼輸入框")
                    break
                except TimeoutException:
                    continue
            
            if not password_input:
                raise Exception("無法找到密碼輸入框")
        
        # 填入登入信息
        print(f"[INFO] 正在填入登入信息...")
        username_input.clear()
        username_input.send_keys(username)
        time.sleep(0.5)
        
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(0.5)
        
        # 提交表單
        password_input.send_keys(Keys.RETURN)
        print("[INFO] 登入表單已提交")
        
        # 等待頁面響應
        time.sleep(3)
        
        # 檢查登入結果
        current_url = driver.current_url
        result['final_url'] = current_url
        
        # 檢查URL是否變化
        if current_url != url:
            print(f"[SUCCESS] 登入成功！頁面跳轉到: {current_url}")
            result['success'] = True
            result['message'] = f"登入成功，頁面跳轉到: {current_url}"
        else:
            # 檢查錯誤訊息
            error_selectors = [
                '.el-form-item__error',
                '.el-message__content',
                '.alert',
                '[role="alert"]',
                '.error',
                '.warning',
                'div[style*="color: red"]'
            ]
            
            for selector in error_selectors:
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for error_element in error_elements:
                        error_text = error_element.text.strip()
                        if error_text and ('錯誤' in error_text or 'error' in error_text.lower() or '失敗' in error_text):
                            print(f"[ERROR] 登入失敗: {error_text}")
                            result['success'] = False
                            result['message'] = f"登入失敗: {error_text}"
                            return result
                except:
                    continue
            
            # 檢查是否仍在登入頁面但沒有明顯錯誤
            print("[WARN] 無法確定登入結果，頁面可能在處理中")
            result['success'] = False
            result['message'] = "登入表單已提交，但無法確認結果"
    
    except Exception as e:
        error_msg = f"登入過程發生錯誤: {str(e)}"
        print(f"[ERROR] {error_msg}")
        result['success'] = False
        result['message'] = error_msg
        result['error'] = str(e)
    
    finally:
        if driver:
            try:
                if detach:
                    # 使用 detach 參數，瀏覽器將在程式結束後保持開啟
                    print("[INFO] 登入完成，瀏覽器將保持開啟狀態")
                    print("[INFO] 瀏覽器將在程式結束後繼續執行，請手動關閉")
                else:
                    # 不使用 detach 參數，等待用戶按 Enter 鍵再關閉
                    print("[INFO] 登入完成，請按 Enter 鍵關閉瀏覽器...")
                    input("按 Enter 鍵退出...")
            except:
                pass
    
    return result

def main():
    """主函數 - 處理命令行參數和執行登入"""
    parser = argparse.ArgumentParser(
        description="Web登入程式 - 專門用於網站登入的Command Line工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python web_login.py -u http://example.com -username admin -password 123456
  python web_login.py -u http://localhost:8080 -username test -password pass -headless False
  python web_login.py -u http://example.com -username user -password pass -username_webid user_id -password_webid pass_id
  python web_login.py -u http://example.com -username user -password pass -username_webid 'input[type="text"]' -password_webid 'input[type="password"]'
  python web_login.py -u http://example.com -username user -password pass -username_webid 'input.el-input__inner[type="text"]' -password_webid 'input.el-input__inner[type="password"]'
  python web_login.py -u http://example.com -username user -password pass -username_webid "input[class=\"el-input__inner\"][type=\"text\"]" -password_webid "input[class=\"el-input__inner\"][type=\"password\"]"
  注意：CSS選擇器請使用正確語法（見說明文件）
        """
    )
    
    # 必要參數
    parser.add_argument('-u', '--url', required=True, help='網站URL')
    parser.add_argument('-username', required=True, help='用戶名')
    parser.add_argument('-password', required=True, help='密碼')
    
    # 可選參數
    parser.add_argument('-username_webid', help='用戶名輸入框的ID或CSS選擇器（可選，含空格將被視為CSS選擇器）')
    parser.add_argument('-password_webid', help='密碼輸入框的ID或CSS選擇器（可選，含空格將被視為CSS選擇器）')
    parser.add_argument('-headless', type=bool, default=False, help='是否使用無頭模式 (預設: False)')
    parser.add_argument('-detach', type=bool, default=True, help='是否在程式結束後保持瀏覽器開啟 (預設: True)')
    parser.add_argument('-timeout', type=int, default=10, help='元素等待超時時間 (預設: 10秒)')
    parser.add_argument('-browser_path', help='Chrome瀏覽器執行檔路徑')
    parser.add_argument('-driver_path', help='ChromeDriver路徑')
    
    # 輸出選項
    parser.add_argument('-v', '--verbose', action='store_true', help='詳細輸出模式')
    parser.add_argument('-j', '--json', action='store_true', help='輸出JSON格式結果')
    
    args = parser.parse_args()
    
    # 執行登入
    print("=" * 50)
    print("Web登入程式")
    print("=" * 50)
    print(f"目標網站: {args.url}")
    print(f"用戶名: {args.username}")
    print(f"無頭模式: {args.headless}")
    print(f"超時設置: {args.timeout}秒")
    if args.verbose:
        print(f"用戶名輸入框ID: {args.username_webid}")
        print(f"密碼輸入框ID: {args.password_webid}")
    print("=" * 50)
    
    # 執行登入
    result = login_website(
        url=args.url,
        username=args.username,
        password=args.password,
        username_webid=args.username_webid,
        password_webid=args.password_webid,
        headless=args.headless,
        timeout=args.timeout,
        browser_path=args.browser_path,
        driver_path=args.driver_path,
        detach=args.detach
    )
    
    # 輸出結果
    print("\n" + "=" * 50)
    print("登入結果")
    print("=" * 50)
    
    if args.json:
        # JSON輸出格式
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 標準輸出格式
        status = "成功" if result['success'] else "失敗"
        print(f"登入狀態: {status}")
        print(f"結果訊息: {result['message']}")
        if result['final_url']:
            print(f"最終URL: {result['final_url']}")
        if result['error']:
            print(f"錯誤詳情: {result['error']}")
    
    # 根據結果設置退出代碼
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()