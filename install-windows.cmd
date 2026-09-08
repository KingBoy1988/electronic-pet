@echo off
REM Electronic Pet - Windows Installer
REM Encoding: ASCII only to avoid CMD garbled text

echo ================================
echo   Electronic Pet - Installer
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo Check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/3] Installing PySide6...
pip install PySide6 -q
if errorlevel 1 (
    echo [ERROR] Failed to install PySide6.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo [2/3] Creating desktop shortcut...
set "TARGET=%~dp0main.py"
set "SHORTCUT=%USERPROFILE%\Desktop\ElectronicPet.lnk"

REM Use PowerShell to create shortcut
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = 'pythonw'; $s.Arguments = '\"%TARGET%\"'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'Electronic Pet Desktop'; $s.Save()"

if exist "%SHORTCUT%" (
    echo Shortcut created successfully!
) else (
    echo [WARNING] Shortcut creation failed.
    echo You can run the pet manually with: pythonw main.py
)

echo [3/3] Done!
echo.
echo Installation complete! Double-click "ElectronicPet" on your desktop to start.
echo Or run: pythonw main.py
echo.
pause
