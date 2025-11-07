# Web登入程式使用說明

## 程式概述

`web_login.py` 是一個專門用於網站登入的 Command Line 工具，基於 `test_login_improved.py` 創建，專注於實際登入操作。

## 功能特色

- **視窗模式**：預設使用視窗模式，顯示瀏覽器
- **瀏覽器保持開啟**：登入完成後瀏覽器不會自動關閉
- **多元素定位策略**：支援ID、CSS選擇器等多種定位方式
- **完整錯誤處理**：詳細的錯誤報告和異常處理
- **多樣化輸出**：支援標準格式和JSON格式輸出
- **靈活配置**：豐富的命令行參數配置選項

## 安裝需求

```bash
pip install selenium
```

## 基本使用

### 語法格式
```bash
python web_login.py -u <URL> -username <用戶名> -password <密碼> [選項]
```

### 必備參數
- `-u, --url`: 目標網站URL
- `-username`: 用戶名
- `-password`: 密碼

### 使用範例

#### 基本登入
```bash
python web_login.py -u http://example.com -username admin -password 123456
```

#### 顯示詳細資訊
```bash
python web_login.py -u http://example.com -username admin -password 123456 -v
```

#### 自定義元素定位
```bash
python web_login.py -u http://example.com -username admin -password 123456 -username_webid user_field -password_webid pass_field
```

#### 使用無頭模式
```bash
python web_login.py -u http://example.com -username admin -password 123456 -headless True
```

#### 設置超時時間
```bash
python web_login.py -u http://example.com -username admin -password 123456 -timeout 20
```

#### JSON輸出格式
```bash
python web_login.py -u http://example.com -username admin -password 123456 -j
```

## 詳細參數說明

### 必要參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `-u, --url` | 目標網站URL | `http://localhost:8080` |
| `-username` | 用戶名 | `admin` |
| `-password` | 密碼 | `password123` |

### 可選參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-username_webid` | 用戶名輸入框的ID | 無 |
| `-password_webid` | 密碼輸入框的ID | 無 |
| `-headless` | 是否使用無頭模式 | `False` |
| `-timeout` | 元素等待超時時間(秒) | `10` |
| `-browser_path` | Chrome瀏覽器路徑 | 無 |
| `-driver_path` | ChromeDriver路徑 | 無 |

### 輸出選項

| 參數 | 說明 |
|------|------|
| `-v, --verbose` | 詳細輸出模式 |
| `-j, --json` | JSON格式輸出 |

## 輸出說明

### 標準輸出格式
```
==================================================
Web登入程式
==================================================
目標網站: http://example.com
用戶名: admin
無頭模式: False
超時設置: 10秒
==================================================
[INFO] 正在打開網站: http://example.com
[INFO] 網站加載完成
[INFO] 使用選擇器 'input[type="text"]' 找到用戶名輸入框
[INFO] 使用選擇器 'input[type="password"]' 找到密碼輸入框
[INFO] 正在填入登入信息...
[INFO] 登入表單已提交
[SUCCESS] 登入成功！頁面跳轉到: http://example.com/dashboard
[INFO] 登入完成，瀏覽器保持開啟狀態
[INFO] 請手動關閉瀏覽器視窗

==================================================
登入結果
==================================================
登入狀態: 成功
結果訊息: 登入成功，頁面跳轉到: http://example.com/dashboard
最終URL: http://example.com/dashboard
```

### JSON輸出格式
```json
{
  "success": true,
  "message": "登入成功，頁面跳轉到: http://example.com/dashboard",
  "final_url": "http://example.com/dashboard",
  "error": null
}
```

## 錯誤處理

程式會自動處理以下常見錯誤：

### 網路連接錯誤
- DNS解析失敗
- 連接超時
- 網路不可達

### 元素定位錯誤
- 用戶名輸入框未找到
- 密碼輸入框未找到
- 元素定位超時

### 登入結果檢測
- URL未變化（可能在登入頁面）
- 錯誤訊息檢測
- 登入狀態無法確認

## 常見問題

### Q: 程式無法找到輸入框怎麼辦？
A: 檢查網站是否有特殊的元素結構，可以使用以下方法：
1. 檢查網頁的HTML源碼
2. 使用瀏覽器開發者工具檢查元素
3. 提供自定義的webid或CSS選擇器

### Q: 登入後頁面沒有跳轉怎麼判斷成功？
A: 程式會嘗試檢測錯誤訊息，如果沒有明顯錯誤且頁面沒有跳轉，會返回"無法確認登入結果"的訊息。

### Q: 程式執行時間過長怎麼辦？
A: 可以調整以下參數：
- 減少 `-timeout` 參數
- 確保網路連接正常
- 檢查目標網站響應速度

### Q: 如何在腳本中使用此程式？
A: 範例腳本：
```bash
#!/bin/bash
# 登入測試
if python web_login.py -u http://example.com -username $USER -password $PASS; then
    echo "登入成功，執行後續操作"
    # 在這裡執行登入後的操作
else
    echo "登入失敗"
    exit 1
fi
```

## 與原程式的差異

| 功能 | test_login_improved.py | web_login.py |
|------|----------------------|--------------|
| 主要用途 | 測試和調試 | 生產環境登入 |
| 介面 | 有測試代碼 | 純命令行程式 |
| 輸出格式 | 簡單輸出 | 詳細輸出+JSON |
| 參數配置 | 硬編碼 | 命令行參數 |
| 錯誤處理 | 基本處理 | 完整錯誤報告 |
| 使用場景 | 開發測試 | 自動化腳本 |

## 退出代碼

- `0`: 登入成功
- `1`: 登入失敗或發生錯誤

## 技術支持

如遇到問題，請檢查：
1. Chrome瀏覽器和ChromeDriver版本是否匹配
2. 網路連接是否正常
3. 目標網站是否可正常訪問
4. 登入信息是否正確

---

*最後更新: 2025-11-07*