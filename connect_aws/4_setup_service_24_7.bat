@echo off
REM ========================================
REM Setup Systemd Service - Run 24/7
REM ========================================

echo.
echo ========================================
echo   Setup YouTube Player as 24/7 Service
echo ========================================
echo.
echo This will configure the app to:
echo   - Run in background 24/7
echo   - Auto-restart on crash
echo   - Auto-start on server reboot
echo   - Keep running when you close SSH
echo.
echo After setup, you can safely close SSH!
echo.
pause

echo.
echo Connecting to server to setup service...
echo.
echo Copy and paste these commands on the server:
echo.
echo ========================================
type "%~dp0setup_systemd_service.txt"
echo ========================================
echo.
pause

ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com
