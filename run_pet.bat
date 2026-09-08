@echo off
REM Electronic Pet - Direct Launcher
REM Just double-click this file to start your pet!

cd /d "%~dp0"
pythonw main.py
if errorlevel 1 (
    echo Failed to start. Trying python instead of pythonw...
    python main.py
    pause
)
