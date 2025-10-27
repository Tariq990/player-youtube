@echo off
REM ========================================
REM 1. Auto Setup - First Time Installation
REM ========================================

echo.
echo ========================================
echo   YouTube Player - Auto Setup
echo   التثبيت التلقائي الكامل
echo ========================================
echo.
echo This will:
echo   [1] Update system
echo   [2] Install Python 3.13
echo   [3] Install Brave Browser
echo   [4] Install Xvfb
echo   [5] Download project from GitHub
echo   [6] Setup Python environment
echo   [7] Configure 24/7 service
echo.
echo Time needed: ~10 minutes
echo.
pause

echo.
echo Uploading setup script to server...
scp -i "C:\Users\tarik\Desktop\meeee.pem" "%~dp0auto_setup.sh" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com:~/

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to upload script!
    pause
    exit /b 1
)

echo.
echo Connecting to server to run installation...
echo.
ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com "chmod +x ~/auto_setup.sh && ~/auto_setup.sh"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ✅ Installation Complete!
    echo ========================================
    echo.
    echo Next: Run 2_upload_cookies.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   ❌ Installation Failed!
    echo ========================================
    echo.
)

pause
