@echo off
REM Electronic Pet - Windows Installer (v2 - robust)
REM No Chinese characters to avoid encoding issues

echo ================================
echo   Electronic Pet - Installer
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found. Version:
python --version

echo.
echo [1/3] Installing PySide6...
pip install PySide6 -q 2>nul
if errorlevel 1 (
    echo Trying with --break-system-packages...
    pip install PySide6 --break-system-packages -q 2>nul
)
echo Done.

echo [2/3] Creating launcher and shortcut...

REM Get script directory
set "SCRIPT_DIR=%~dp0"

REM Create a VBS script to make the shortcut
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\ElectronicPet.lnk"
set "TARGET_PATH=%SCRIPT_DIR%run_pet.bat"

REM Write VBS file
echo Set ws = CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo Set shortcut = ws.CreateShortcut("%SHORTCUT_PATH%") >> "%VBS_SCRIPT%"
echo shortcut.TargetPath = "%TARGET_PATH%" >> "%VBS_SCRIPT%"
echo shortcut.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_SCRIPT%"
echo shortcut.Description = "Electronic Pet Desktop" >> "%VBS_SCRIPT%"
echo shortcut.IconLocation = "shell32.dll,137" >> "%VBS_SCRIPT%"
echo shortcut.Save >> "%VBS_SCRIPT%"

REM Run VBS to create shortcut
cscript //nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

REM Check result
if exist "%SHORTCUT_PATH%" (
    echo Desktop shortcut created successfully!
) else (
    echo [WARNING] Shortcut creation failed. You can still run run_pet.bat directly.
)

echo [3/3] Done!
echo.
echo ================================
echo  Installation Complete!
echo ================================
echo.
echo How to start your pet:
echo   Option 1: Double-click "ElectronicPet" on your desktop
echo   Option 2: Double-click "run_pet.bat" in this folder
echo.
pause
