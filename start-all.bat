@echo off
echo Starting all services...
start cmd /k "cd backend && node server.js"

echo wait 3 second ...
timeout /t 3 /nobreak > null

echo Starting frontend services...
start cmd /k "cd frontend && npm start"

echo Services started successfully!
echo Backend: http://localhost:3001
echo Frontend: http://localhost:3000
```