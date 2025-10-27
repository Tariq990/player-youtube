@echo off
REM ========================================
REM 3. Manage 24/7 Service
REM ========================================

:menu
cls
echo.
echo ========================================
echo   YouTube Player - Service Manager
echo   ادارة الخدمة 24/7
echo ========================================
echo.
echo [1] Start Service       (تشغيل الخدمة)
echo [2] Stop Service        (ايقاف الخدمة)
echo [3] Restart Service     (اعادة تشغيل)
echo [4] Check Status        (حالة الخدمة)
echo [5] View Live Logs      (مشاهدة السجلات)
echo [6] View Last 50 Lines  (آخر 50 سطر)
echo [0] Exit                (خروج)
echo.
echo ========================================
set /p choice="اختر رقم: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto logs_live
if "%choice%"=="6" goto logs_last
if "%choice%"=="0" exit
goto menu

:start
echo.
echo تشغيل الخدمة...
ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com "sudo systemctl start youtube-player && sudo systemctl status youtube-player"
pause
goto menu

:stop
echo.
echo ايقاف الخدمة...
ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com "sudo systemctl stop youtube-player && sudo systemctl status youtube-player"
pause
goto menu

:restart
echo.
echo اعادة تشغيل الخدمة...
ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com "sudo systemctl restart youtube-player && sudo systemctl status youtube-player"
pause
goto menu

:status
echo.
echo حالة الخدمة:
ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com "sudo systemctl status youtube-player"
pause
goto menu

:logs_live
echo.
echo مشاهدة السجلات المباشرة (Ctrl+C للخروج)
ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com "sudo journalctl -u youtube-player -f"
pause
goto menu

:logs_last
echo.
echo آخر 50 سطر من السجلات:
ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com "sudo journalctl -u youtube-player -n 50 --no-pager"
pause
goto menu
