# 資料庫工具程式 - 使用說明

## 專案概述

這是一個使用 Python + PyQt5 + MySQL 開發的資料庫工具程式，主要用於管理和查詢命令工具、提示工具、Windows 程式和網站管理四張資料表。程式提供直觀的圖形界面，支援資料的檢視、篩選、編輯和匯出功能。

## 功能特色

### 📊 資料管理
- **四資料表支援**: CmdTools（命令工具）、PromptTools（提示工具）、WinProgram（Windows 程式）和 WebSite（網站管理）
- **分頁界面**: 使用 Tab 切換不同資料表
- **即時載入**: 程式啟動時自動載入所有資料到記憶體
- **本地篩選**: 篩選操作在本地執行，響應快速

### 🔍 搜尋篩選
- **全域搜尋**: 頂部搜尋框可搜尋所有表格的所有欄位
- **單一欄位搜尋**: 每個表格的每個欄位都有獨立的搜尋框
- **即時搜尋**: 輸入時自動搜尋，無需點擊按鈕
- **清除功能**: 每個搜尋框都有清除按鈕

### ✏️ 資料編輯
- **新增記錄**: 點擊新增按鈕或右鍵選單新增資料
- **編輯記錄**: 雙擊表格項目或點擊編輯按鈕修改資料
- **刪除記錄**: 選擇記錄後點擊刪除按鈕，會有確認對話框
- **資料驗證**: 輸入驗證，確保必填欄位不為空

### 📤 資料匯出
- **JSON 格式匯出**: 將資料匯出為標準 JSON 格式
- **彈性匯出範圍**: 可選擇匯出篩選結果或全部資料
- **詳細資訊**: 匯出的 JSON 包含匯出時間、資料表名稱、記錄數量等資訊

### 🎨 使用者介面
- **繁體中文介面**: 全中文使用者介面
- **現代化設計**: 採用現代化的 UI 設計
- **狀態列**: 顯示連線狀態和資料統計
- **進度指示**: 資料載入時顯示進度條

## 系統需求

### 軟體需求
- **Python**: 3.7 或更高版本
- **MySQL**: 5.7 或更高版本
- **作業系統**: Windows、macOS、Linux

### Python 套件依賴
```
PyQt5>=5.15.0
mysql-connector-python>=8.0.0
```

## 安裝指南

### 1. 下載程式
```bash
# 如果是從 Git 儲存庫下載
git clone <repository-url>
cd cmdtools-gui
```

### 2. 安裝依賴套件
```bash
# 使用 pip 安裝依賴
pip install -r requirements.txt

# 或者手動安裝
pip install PyQt5 mysql-connector-python
```

### 3. 設定資料庫連線
編輯 `config.json` 檔案，設定您的資料庫連線資訊：

```json
{
  "DBServer": "127.0.0.1",
  "DBPort": "3306",
  "DBUser": "您的資料庫用戶名",
  "DBPassword": "您的資料庫密碼",
  "DataBase": "MyCmdTools"
}
```

### 4. 確保資料表存在
確保您的 MySQL 資料庫中存在以下四張資料表：

#### CmdTools 資料表
```sql
CREATE TABLE IF NOT EXISTS `CmdTools` (
  `iSeqNo` int(11) NOT NULL AUTO_INCREMENT,
  `cmd` varchar(150) DEFAULT NULL,
  `example` varchar(150) DEFAULT NULL,
  `remark1` varchar(150) DEFAULT NULL,
  `Classification` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`iSeqNo`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

#### PromptTools 資料表
```sql
CREATE TABLE IF NOT EXISTS `PromptTools` (
  `iSeqNo` int(11) NOT NULL AUTO_INCREMENT,
  `Prompt` text DEFAULT NULL,
  `Prompt_Eng` text DEFAULT NULL,
  `Classification` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`iSeqNo`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

#### WinProgram 資料表
```sql
CREATE TABLE IF NOT EXISTS `WinProgram` (
  `iSeqNo` INT(11) NOT NULL AUTO_INCREMENT,
  `remark1` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
  `ProgramPathAndName` VARCHAR(150) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
  `ClickEndRun` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`iSeqNo`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

#### WebSite 資料表
```sql
CREATE TABLE IF NOT EXISTS `WebSite` (
  `iSeqNo` INT(11) NOT NULL AUTO_INCREMENT,
  `Remark` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
  `Classification` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
  `Website` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
  `account` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
  `password` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
  PRIMARY KEY (`iSeqNo`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

## 使用指南

### 啟動程式
```bash
python main.py
```

### 主要功能操作

#### 1. 全域搜尋
- 在頂部的搜尋框輸入關鍵字
- 程式會即時搜尋所有表格的所有欄位
- 點擊「搜尋」按鈕手動觸發搜尋
- 點擊「清除」按鈕清除搜尋條件

#### 2. 分頁切換
- 點擊「命令工具」分頁查看 CmdTools 資料
- 點擊「提示工具」分頁查看 PromptTools 資料
- 點擊「Windows 程式」分頁查看 WinProgram 資料
- 點擊「網站管理」分頁查看 WebSite 資料

#### 3. 單一欄位搜尋
在每個分頁中：
- 每個欄位都有對應的搜尋框
- 輸入關鍵字進行精確搜尋
- 點擊「搜尋」按鈕執行搜尋
- 點擊「清除」按鈕清除該欄位搜尋

#### 4. 資料編輯
- **新增資料**: 點擊「新增」按鈕，填寫表單後點擊「確定」
- **編輯資料**: 選中記錄後點擊「編輯」按鈕，或雙擊表格項目
- **刪除資料**: 選中記錄後點擊「刪除」按鈕，確認後執行刪除

#### 5. 資料匯出
- 點擊「匯出」按鈕
- 選擇匯出範圍（篩選結果或全部資料）
- 設定檔案名稱和位置
- 點擊「匯出」執行匯出

#### 6. 資料更新
- **刷新資料**: 點擊「刷新資料」按鈕重新從資料庫載入資料
- **更新資料庫**: 點擊「更新資料庫」按鈕確保資料庫同步

#### 7. Windows 程式分頁功能
- **執行按鈕**: 當「點擊後執行」屬性設為「是」（值為 1）時，顯示執行按鈕
- **按鈕行為**:
  - 根據選中的記錄動態啟用/禁用
  - 顯示程式名稱：「執行程式: [程式名稱]」
  - 支援跨平台執行（Windows、Linux、Mac）
  - 自動檢查程式檔案存在性
  - 嘗試不同副檔名 (.exe, .bat, .cmd)
  - 在系統 PATH 中搜索程式
- **狀態指示**：提供即時狀態訊息和視覺反饋

#### 8. 網站管理分頁功能
- **開啟網站按鈕**: 為網站管理分頁添加直接開啟網站的功能
- **按鈕行為**:
  - 根據選中的記錄動態啟用/禁用
  - 顯示網站域名：「開啟網站: [網站域名]」
  - 自動添加 https:// 協議（如果缺失）
  - 使用系統默認瀏覽器開啟網站
- **狀態指示**：提供即時狀態訊息和視覺反饋

## 資料格式說明

### CmdTools 資料表欄位
- **iSeqNo**: 序號（自動產生）
- **cmd**: 命令內容
- **example**: 使用範例
- **remark1**: 備註1
- **Classification**: 類型分類

### PromptTools 資料表欄位
- **iSeqNo**: 序號（自動產生）
- **Prompt**: 提示內容（中文）
- **Prompt_Eng**: 提示內容（英文）
- **Classification**: 分類標籤

### WinProgram 資料表欄位
- **iSeqNo**: 序號（自動產生）
- **remark1**: 備註1
- **ProgramPathAndName**: 程式路徑與名稱
- **ClickEndRun**: 點擊後執行（0:否，1:是）

### WebSite 資料表欄位
- **iSeqNo**: 序號（自動產生）
- **Remark**: 備註
- **Classification**: 分類
- **Website**: 網站網址
- **account**: 帳號
- **password**: 密碼

### 匯出 JSON 格式
```json
{
  "export_time": "2025-11-06T07:31:00.000Z",
  "table_name": "CmdTools",
  "total_records": 10,
  "filtered_records": 5,
  "data": [
    {
      "iSeqNo": 1,
      "cmd": "example command",
      "example": "example usage",
      "remark1": "note 1",
      "remark2": "note 2",
      "Classification": "command type"
    }
  ]
}
```

## 疑難排解

### 常見問題

#### 1. 資料庫連線失敗
**問題**: 程式啟動時顯示連線失敗
**解決方案**:
- 檢查 `config.json` 中的資料庫連線設定
- 確認 MySQL 服務正在運行
- 確認資料庫用戶具有適當權限
- 檢查防火牆設定

#### 2. 套件安裝失敗
**問題**: 安裝 PyQt5 或 mysql-connector-python 時失敗
**解決方案**:
```bash
# 升級 pip
python -m pip install --upgrade pip

# 使用國內鏡像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 3. 程式無法啟動
**問題**: 執行 `python main.py` 時出現錯誤
**解決方案**:
- 檢查 Python 版本（需要 3.7+）
- 確認所有依賴套件已正確安裝
- 檢查檔案權限

#### 4. 搜尋功能異常
**問題**: 搜尋結果不正確或不顯示
**解決方案**:
- 檢查資料編碼設定
- 確認資料表中的資料格式正確
- 重新載入資料（點擊刷新按鈕）

#### 5. 程式執行功能異常
**問題**: 執行程式時發生錯誤
**解決方案**:
- 確認程式路徑正確
- 檢查程式檔案是否存在
- 確認程式具有執行權限

#### 6. 網站開啟功能異常
**問題**: 開啟網站時發生錯誤
**解決方案**:
- 確認網站網址正確
- 檢查網路連線
- 確認系統默認瀏覽器設置正確

### 錯誤代碼說明

- **連線失敗**: 資料庫連線設定錯誤或服務不可用
- **載入錯誤**: 資料庫讀取失敗或資料表不存在
- **操作失敗**: 資料操作（新增/編輯/刪除）執行失敗
- **匯出失敗**: 檔案權限不足或磁碟空間不足
- **執行失敗**: 程式執行時發生錯誤
- **網站開啟失敗**: 網站開啟時發生錯誤

## 開發資訊

### 程式架構
```
cmdtools_gui/
├── __init__.py          # 套件初始化
├── database.py          # 資料庫操作模組
├── main_window.py       # 主視窗程式
├── table_widget.py      # 表格顯示模組
├── dialogs.py          # 對話框模組
main.py                 # 主程式入口
config.json            # 資料庫設定
requirements.txt       # 依賴套件清單
```

### 技術特色
- **模組化設計**: 功能模組清晰分離，便於維護
- **異步處理**: UI 操作與資料庫操作分離，提升響應性
- **錯誤處理**: 完整的異常處理機制
- **可擴展性**: 架構支援功能擴展和客製化

## 聯絡資訊

如有問題或建議，請聯絡開發者或提交 Issue。

---
**版本**: 1.0.0  
**最後更新**: 2025-11-07
**開發者**: Roo & Porter