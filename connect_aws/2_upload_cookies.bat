@echo off@echo off

REM ========================================REM ========================================

REM 2. Upload/Update CookiesREM Step 2: Upload cookies.json to Server

REM ========================================REM ========================================



echo.echo.

echo ========================================echo ========================================

echo   Upload/Update Cookiesecho   Step 2: Upload Cookies to Server

echo   رفع او تحديث الكوكيزecho ========================================

echo ========================================echo.

echo.echo Make sure setup is complete on server!

echo Auto-reload: The server will detectecho.

echo the change and reload automatically!pause

echo (No restart needed)

echo.scp -i "C:\Users\tarik\Desktop\meeee.pem" "C:\Users\tarik\Desktop\youtube player\data\cookies.json" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com:~/player-youtube/data/

pause

if %errorlevel% equ 0 (

echo.    echo.

echo Uploading cookies.json...    echo ========================================

scp -i "C:\Users\tarik\Desktop\meeee.pem" "C:\Users\tarik\Desktop\youtube player\data\cookies.json" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com:~/player-youtube/data/    echo   ✅ Cookies uploaded successfully!

    echo ========================================

if %errorlevel% equ 0 (    echo.

    echo.    echo Next step: Run 3_start_application.bat

    echo ========================================    echo.

    echo   ✅ Cookies Uploaded!) else (

    echo ========================================    echo.

    echo.    echo ========================================

    echo The server will auto-reload within 2 seconds    echo   ❌ Upload failed!

    echo Watch server logs for:    echo ========================================

    echo   "🔄 Cookies reloaded: X active sets"    echo.

    echo.    echo Possible issues:

) else (    echo 1. Setup not complete on server

    echo.    echo 2. player-youtube folder doesn't exist

    echo ========================================    echo.

    echo   ❌ Upload Failed!    echo Solution: Make sure you ran all commands

    echo ========================================    echo from setup_server_commands.txt on the server

    echo.    echo.

    echo Make sure:)

    echo 1. Server is accessible

    echo 2. Setup completed (run 1_SETUP_FIRST_TIME.bat)pause

    echo 3. cookies.json exists in data/ folder
    echo.
)

pause
