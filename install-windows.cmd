@echo off
chcp 65001 >nul
title 电子宠物安装

echo ================================
echo   电子宠物 - 安装程序
echo ================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/3] 安装依赖中...
pip install PySide6 -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络
    pause
    exit /b 1
)

echo [2/3] 创建快捷方式...
set "TARGET=%~dp0main.py"
set "SHORTCUT=%USERPROFILE%\Desktop\电子宠物.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = 'pythonw'; $s.Arguments = '"%TARGET%"'; $s.WorkingDirectory = '%~dp0'; $s.IconLocation = 'pythonw.exe,0'; $s.Description = '电子宠物桌面应用'; $s.Save()"

echo [3/3] 安装完成！
echo.
echo 桌面上已创建"电子宠物"快捷方式，双击即可运行。
echo.
pause
