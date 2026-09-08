@echo off
REM Electronic Pet - Diagnostic Tool
REM This will show all errors so we can fix them

echo ================================
echo   Electronic Pet - Diagnostic
echo ================================
echo.

echo [1] Checking Python...
echo --------------------------------
where python 2>nul
if errorlevel 1 (
    echo [FAIL] Python not found in PATH!
    echo.
    echo Trying python3...
    where python3 2>nul
    if errorlevel 1 (
        echo [FAIL] python3 also not found!
        echo.
        echo ================================
        echo  ROOT CAUSE: Python is not installed
        echo  or not added to PATH.
        echo  
        echo  FIX: Install Python from:
        echo  https://www.python.org/downloads/
        echo  Check "Add Python to PATH" during install!
        echo ================================
        goto end
    ) else (
        echo python3 found!
    )
)

echo.
echo Python version:
python --version 2>&1
if errorlevel 1 python3 --version 2>&1

echo.
echo [2] Checking pip...
echo --------------------------------
python -m pip --version 2>&1
if errorlevel 1 (
    echo [FAIL] pip not found
    goto end
)

echo.
echo [3] Checking PySide6...
echo --------------------------------
python -c "import PySide6; print('PySide6 version:', PySide6.__version__)" 2>&1
if errorlevel 1 (
    echo [FAIL] PySide6 not installed!
    echo.
    echo Attempting to install PySide6...
    python -m pip install PySide6 2>&1
    echo.
    echo Checking again...
    python -c "import PySide6; print('PySide6 OK:', PySide6.__version__)" 2>&1
    if errorlevel 1 (
        echo [FAIL] PySide6 installation failed!
        goto end
    )
)

echo.
echo [4] Testing pet application...
echo --------------------------------
cd /d "%~dp0"
echo Working directory: %CD%
echo.
echo Files in current directory:
dir /b *.py src\*.py 2>nul

echo.
echo Starting pet with error output visible...
echo --------------------------------
python main.py 2>&1

echo.
echo --------------------------------
echo Diagnostic complete.
echo If you see any [FAIL] or error messages above,
echo please take a screenshot and send it back.

:end
echo.
pause
