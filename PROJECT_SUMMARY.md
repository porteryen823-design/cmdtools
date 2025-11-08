# React 前端 + Express 後端 + MySQL 資料表工具

## 專案概述
本專案旨在設計並實作一個使用 React 作為前端，透過後端 Express API 連接 MySQL 資料庫的工具，以表格形式顯示資料。

## 技術棧
- 前端：React
- 後端：Node.js + Express
- 資料庫：MySQL (使用模擬資料進行測試)

## 專案結構
```
project/
├── backend/
│   ├── server.js           # Express 伺服器
│   ├── package.json        # 後端依賴
│   └── node_modules/       # 依賴套件
└── frontend/
    ├── src/
    │   ├── App.js          # React 主應用程式
    │   └── index.js        # 入口檔案
    ├── public/
    │   └── index.html      # HTML 模板
    ├── package.json        # 前端依賴
    └── node_modules/       # 依賴套件
```

## 功能
- 後端 API 提供 `/api/data` 路由，回傳 JSON 格式的資料
- 前端 React 應用程式從 API 取得資料，並在表格中顯示

## 安裝與執行

1. 安裝後端依賴：
   ```
   cd backend
   npm install
   ```

2. 啟動後端伺服器：
   ```
   npm start
   ```

3. 安裝前端依賴：
   ```
   cd frontend
   npm install
   ```

4. 啟動前端應用程式：
   ```
   npm start
   ```

## API 說明
- URL: `http://localhost:3001/api/data`
- 方法: GET
- 回傳: JSON 陣列，包含 id、name、age、email 欄位

## 前端功能
- 使用 axios 發送 GET 請求取得 API 資料
- 載入時顯示「載入中...」
- 發生錯誤時顯示錯誤訊息
- 成功取得資料後以表格形式顯示所有欄位

## 現況
- 後端 API 成功啟動並提供資料
- 前端 React 應用程式架構已完成，但遇到啟動問題
- 專案文件及架構已完成

## 下一步
- 解決前端啟動問題
- 測試前端能否正確顯示後端資料
- 整合前後端，確保系統正常運作