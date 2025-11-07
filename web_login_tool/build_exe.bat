@echo off
echo 正在編譯 web_login.py 成執行檔...

REM 進入 web_login_tool 目錄
cd /d "%~dp0"

REM 清理舊的編譯檔案
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

echo 正在使用 PyInstaller 編譯...
pyinstaller --onefile --name "web_login" --distpath "dist" web_login.py

if %errorlevel% equ 0 (
    echo 編譯成功！執行檔位於 dist\web_login.exe
    echo.
    echo 檔案大小：
    dir "dist\web_login.exe"
) else (
    echo 編譯失敗！
    pause
    exit /b 1
)

echo.
echo 編譯完成！按任意鍵退出...
pause >nul