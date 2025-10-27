@echo off
REM ========================================
REM Update Cookies on Running Server
REM (No need to restart - auto-reload!)
REM ========================================

echo.
echo ========================================
echo   Update Cookies on AWS Server
echo ========================================
echo.
echo This will upload new cookies.json
echo The server will auto-reload them!
echo (No restart needed)
echo.
pause

echo.
echo Uploading cookies.json...
scp -i "C:\Users\tarik\Desktop\meeee.pem" "C:\Users\tarik\Desktop\youtube player\data\cookies.json" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com:~/player-youtube/data/

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ✅ Cookies Updated Successfully!
    echo ========================================
    echo.
    echo The server will automatically:
    echo   - Detect the file change
    echo   - Reload cookies within 2 seconds
    echo   - Continue running without restart
    echo.
    echo Check server logs to confirm:
    echo   "🔄 Cookies reloaded: X active sets"
    echo.
) else (
    echo.
    echo ========================================
    echo   ❌ Upload Failed!
    echo ========================================
    echo.
    echo Possible issues:
    echo 1. Server is not running
    echo 2. SSH connection problem
    echo 3. File path incorrect
    echo.
)

pause
