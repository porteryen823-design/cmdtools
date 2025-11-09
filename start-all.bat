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