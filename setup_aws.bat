@echo off
REM ========================================
REM AWS EC2 Setup Script for YouTube Player
REM ========================================

echo.
echo ========================================
echo   AWS EC2 YouTube Player Setup
echo ========================================
echo.

REM Change to the directory where meeee.pem is located
cd /d "%~dp0"

echo Step 1: Setting permissions on meeee.pem...
echo (Windows doesn't need chmod, but make sure file is not read-only)
attrib -r meeee.pem 2>nul
echo.

echo Step 2: Connecting to AWS EC2 Instance...
echo Instance: i-0bc2fbfadd2aec25b
echo Region: eu-north-1 (Stockholm)
echo.
echo Press CTRL+C to cancel, or
pause

echo.
echo Connecting via SSH...
ssh -i "meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com

REM If SSH fails, show troubleshooting
if errorlevel 1 (
    echo.
    echo ========================================
    echo   SSH Connection Failed!
    echo ========================================
    echo.
    echo Possible solutions:
    echo 1. Make sure meeee.pem is in the same folder as this script
    echo 2. Check if EC2 instance is running in AWS Console
    echo 3. Verify Security Group allows SSH (port 22) from your IP
    echo 4. Try using PuTTY if OpenSSH is not installed
    echo.
    pause
)
