@echo off
REM ========================================
REM Step 3: Connect and Start Application
REM ========================================

echo.
echo ========================================
echo   Step 3: Start YouTube Player
echo ========================================
echo.
echo After connecting, run these commands:
echo.
echo   cd ~/player-youtube
echo   source venv/bin/activate
echo   xvfb-run -a python3.13 src/app.py
echo.
echo Press Ctrl+C to stop the application
echo.
pause

ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com
