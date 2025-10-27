@echo off
REM ========================================
REM Step 2: Upload cookies.json to Server
REM ========================================

echo.
echo ========================================
echo   Step 2: Upload Cookies to Server
echo ========================================
echo.
echo Make sure setup is complete on server!
echo.
pause

scp -i "C:\Users\tarik\Desktop\meeee.pem" "C:\Users\tarik\Desktop\youtube player\data\cookies.json" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com:~/player-youtube/data/

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ✅ Cookies uploaded successfully!
    echo ========================================
    echo.
    echo Next step: Run 3_start_application.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   ❌ Upload failed!
    echo ========================================
    echo.
    echo Possible issues:
    echo 1. Setup not complete on server
    echo 2. player-youtube folder doesn't exist
    echo.
    echo Solution: Make sure you ran all commands
    echo from setup_server_commands.txt on the server
    echo.
)

pause
