@echo off
REM YouTube Player - Quick Start Script
REM This script helps you get started quickly

echo ============================================================
echo     YouTube Player - Quick Start
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
    echo.
) else (
    echo [1/5] Virtual environment already exists
    echo.
)

REM Activate venv
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install requirements
echo [3/5] Installing/updating packages...
pip install -r requirements.txt --quiet --disable-pip-version-check
echo.

REM Check if .env exists
if not exist ".env" (
    echo [4/5] .env file not found!
    echo.
    echo Please create .env file:
    echo   1. copy .env.example .env
    echo   2. Edit .env and add your ENCRYPTION_KEY
    echo.
    pause
    exit /b 1
) else (
    echo [4/5] .env file exists
    echo.
)

REM Check if cookies exist
if not exist "data\cookies.json" (
    echo [5/5] No cookies found!
    echo.
    echo Run this command to save cookies:
    echo   python scripts\save_cookies.py
    echo.
    pause
    exit /b 1
) else (
    echo [5/5] Cookies found
    echo.
)

echo ============================================================
echo     All checks passed! Ready to start
echo ============================================================
echo.
echo What would you like to do?
echo.
echo [1] Test cookies
echo [2] Run quick test (single video)
echo [3] Start full application
echo [4] Save new cookies
echo [5] Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running cookie test...
    python scripts\test_cookies.py
) else if "%choice%"=="2" (
    echo.
    echo Running quick test...
    python scripts\quick_test.py
) else if "%choice%"=="3" (
    echo.
    echo Starting full application...
    python src\app.py
) else if "%choice%"=="4" (
    echo.
    echo Saving new cookies...
    python scripts\save_cookies.py
) else if "%choice%"=="5" (
    echo.
    echo Exiting...
    exit /b 0
) else (
    echo.
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
pause
