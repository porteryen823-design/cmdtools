# 前端網頁啟動指南

## 📋 啟動步驟

### 1. 前置條件檢查
在啟動前端之前，請確保：
- ✅ Node.js 已安裝 (建議版本 16+)
- ✅ npm 或 yarn 已安裝
- ✅ 後端服務已啟動 (Node.js backend 在 port 3001)
- ✅ MySQL 資料庫服務運行中

### 2. 檢查後端服務
首先確認後端服務是否運行：
```bash
# 測試後端健康狀態
curl http://localhost:3001/health
```

如果返回 `{"status":"healthy","database":"connected"}` 表示後端正常。

### 3. 啟動前端服務
```bash
# 進入前端目錄
cd frontend

# 安裝依賴套件 (首次運行時)
npm install

# 啟動開發服務器
npm start
```

### 4. 訪問前端網頁
啟動成功後，前端會自動在瀏覽器中打開，或手動訪問：
```
http://localhost:3000
```

## 🚀 完整啟動流程

### 方案一：分別啟動 (推薦)
```bash
# 1. 啟動後端 (Terminal 1)
cd backend
node server.js

# 2. 啟動前端 (Terminal 2) 
cd frontend
npm start
```

### 方案二：一鍵啟動腳本
創建啟動腳本 `start-all.bat` (Windows):
```batch
@echo off
echo 啟動後端服務...
start cmd /k "cd backend && node server.js"

echo 等待3秒...
timeout /t 3 /nobreak > null

echo 啟動前端服務...
start cmd /k "cd frontend && npm start"

echo 服務啟動完成！
echo 後端: http://localhost:3001
echo 前端: http://localhost:3000
```

或 `start-all.sh` (Linux/Mac):
```bash
#!/bin/bash
echo "啟動後端服務..."
cd backend && node server.js &
sleep 3
echo "啟動前端服務..."
cd frontend && npm start
```

## 🔧 啟動參數 (可選)

### 前端環境變量
如果後端不在 localhost:3001，創建 `.env` 文件：
```env
REACT_APP_API_BASE_URL=http://your-backend-host:3001
```

### 端口衝突解決
如果 3000 端口被佔用：
```bash
# 設定不同端口
PORT=3002 npm start
```

### 生產環境建置
```bash
# 建置生產版本
npm run build

# 預覽建置結果
npm run serve
```

## ❗ 常見問題

### Q1: npm start 失敗
**解決方案**:
```bash
# 清除 npm 緩存
npm cache clean --force

# 刪除 node_modules 重新安裝
rm -rf node_modules
npm install
```

### Q2: 端口被佔用
**解決方案**:
```bash
# 查看佔用端口的進程
netstat -ano | findstr :3000

# 終止進程 (Windows)
taskkill /PID [進程ID] /F

# 終止進程 (Linux/Mac)  
kill -9 [進程ID]
```

### Q3: 後端連接失敗
**檢查清單**:
- [ ] 後端服務是否在運行
- [ ] 端口 3001 是否可用
- [ ] MySQL 資料庫連接是否正常
- [ ] 防火牆設定

### Q4: 資料載入失敗
**檢查後端 API**:
```bash
# 測試資料API
curl http://localhost:3001/api/data

# 測試健康檢查
curl http://localhost:3001/health
```

### Q5: 瀏覽器顯示空白頁
**解決方案**:
1. 打開瀏覽器開發者工具 (F12)
2. 檢查 Console 是否有錯誤
3. 確認 Network 標籤中的 API 請求是否成功
4. 清除瀏覽器快取

## 📱 行動裝置測試
在區域網路中可通過 IP 訪問：
```bash
# 獲取本機 IP
ipconfig  # Windows
ifconfig  # Linux/Mac

# 其他裝置訪問 (假設 IP 為 192.168.1.100)
http://192.168.1.100:3000
```

## 🎯 成功標誌
當前端成功啟動時，應該看到：
- ✅ 瀏覽器自動打開或可以正常訪問 http://localhost:3000
- ✅ 顯示 "命令工具管理系統" 標題
- ✅ 顯示資料庫連接狀態 (綠色●已連接)
- ✅ 顯示多個資料表分頁 (命令工具、提示工具等)
- ✅ 載入真實的 MySQL 資料而非模擬資料

## 🏗️ 建置生產版本
```bash
# 建置生產版本
cd frontend
npm run build

# 建置後的文件在 build/ 目錄
# 可以部署到任何靜態文件服務器
```

**總結**: 前端網頁通過 `npm start` 啟動，預設運行在 http://localhost:3000，需要確保後端服務 (http://localhost:3001) 和 MySQL 資料庫正常運行。