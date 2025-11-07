# -*- coding: utf-8 -*-
"""
測試登入網頁的腳本
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

from selenium.webdriver.common.keys import Keys

def test_login_website(url, username, password, username_webid=None, password_webid=None):
    """
    測試登入網站功能
    
    Args:
        url: 網站URL
        username: 用戶名
        password: 密碼
        username_webid: 用戶名輸入框的ID（可選）
        password_webid: 密碼輸入框的ID（可選）
    
    Returns:
        成功或失敗的訊息
    """
    driver = None
    try:
        # 創建Chrome驅動實例
        options = webdriver.ChromeOptions()
        # 如果需要無頭模式，請取消註解下面這行
        # options.add_argument('headless')
        options.add_argument('disable-gpu')
        
        # 如果Chrome驅動路徑不在系統PATH中，需要指定路徑
        # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        # driver = webdriver.Chrome(options=options, executable_path=r"path\to\chromedriver.exe")
        
        # 正常創建驅動實例
        driver = webdriver.Chrome(options=options)
        
        # 打開網站
        driver.get(url)
        print(f"已打開網站: {url}")
        
        # 等待網站加載
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[type="email"]'))
            )
            print("網站加載成功，找到用戶名輸入框")
        except TimeoutException:
            print("網站加載失敗或未找到用戶名輸入框")
            return "網站加載失敗或未找到用戶名輸入框"
        
        # 定位用戶名輸入框
        try:
            # 首先嘗試使用ID定位（如果有提供）
            if username_webid:
                try:
                    username_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, username_webid))
                    )
                    print(f"使用ID {username_webid} 找到用戶名輸入框")
                except (TimeoutException, NoSuchElementException):
                    # 如果ID定位失敗，回退到CSS選擇器
                    username_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[type="email"]'))
                    )
                    print(f"ID定位失敗，使用通用選擇器找到用戶名輸入框")
            else:
                # 如果沒有提供ID，使用CSS選擇器
                username_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input.el-input__inner[type="text"]'))
                )
                print("使用CSS選擇器找到用戶名輸入框")
        except TimeoutException:
            # 如果找不到特定的類選擇器，嘗試更通用的選擇器
            try:
                username_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
                )
                print("使用通用選擇器找到用戶名輸入框")
            except TimeoutException:
                print("無法找到用戶名輸入框")
                return "無法找到用戶名輸入框"
        
        # 定位密碼輸入框
        try:
            # 首先嘗試使用ID定位（如果有提供）
            if password_webid:
                try:
                    password_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, password_webid))
                    )
                    print(f"使用ID {password_webid} 找到密碼輸入框")
                except (TimeoutException, NoSuchElementException):
                    # 如果ID定位失敗，回退到CSS選擇器
                    password_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
                    )
                    print(f"ID定位失敗，使用通用選擇器找到密碼輸入框")
            else:
                # 如果沒有提供ID，使用CSS選擇器
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input.el-input__inner[type="password"]'))
                )
                print("使用CSS選擇器找到密碼輸入框")
        except TimeoutException:
            # 如果找不到特定的類選擇器，嘗試更通用的選擇器
            try:
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
                )
                print("使用通用選擇器找到密碼輸入框")
            except TimeoutException:
                print("無法找到密碼輸入框")
                return "無法找到密碼輸入框"
        
        # 填入用戶名
        username_input.clear()
        username_input.send_keys(username)
        print(f"已填入用戶名: {username}")
        time.sleep(1)
        # 填入密碼
        password_input.clear()
        password_input.send_keys(password)
        print("已填入密碼")
        time.sleep(1)
        # 提交表單
        #password_input.submit()
        password_input.send_keys(Keys.RETURN)
        print("已提交登錄表單")
        
        # 等待頁面跳轉或登錄結果
        time.sleep(3)
        
        # 檢查是否登錄成功（可以根據實際網站判斷）
        # 這裡簡單地檢查當前URL是否變化
        current_url = driver.current_url
        if current_url != url:
            print(f"登錄成功！頁面已跳轉到: {current_url}")
            return "登錄成功！頁面已跳轉到: " + current_url
        else:
            # 嘗試查找錯誤信息或成功提示
            try:
                # 查找錯誤信息
                error_elements = driver.find_elements(By.CSS_SELECTOR, '.el-form-item__error, .el-message__content, .alert, [role="alert"]')
                if error_elements:
                    error_text = error_elements[0].text.strip()
                    if error_text:
                        print(f"登錄失敗，錯誤信息: {error_text}")
                        return f"登錄失敗，錯誤信息: {error_text}"
            except NoSuchElementException:
                pass
            
            print("登錄表單已提交，但無法確認登錄結果")
            return "登錄表單已提交，但無法確認登錄結果"
            
    except Exception as e:
        print(f"登錄過程中發生錯誤: {str(e)}")
        return f"登錄過程中發生錯誤: {str(e)}"
    finally:
        # 關閉瀏覽器
        if driver:
            #driver.quit()
            print("已關閉瀏覽器")

# 主程序
if __name__ == "__main__":
    # 測試登入
    url = "http://localhost:18083/"
    username = "admin"
    password = "gsi5613686#"
    
    print("正在測試登入網站...")
    result = test_login_website(url, username, password)
    print(f"測試結果: {result}")