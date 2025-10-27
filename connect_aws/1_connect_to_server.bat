@echo off
REM ========================================
REM Step 1: Connect to AWS EC2 Instance
REM ========================================

echo.
echo ========================================
echo   Step 1: Connect to AWS EC2
echo ========================================
echo.
echo Instance: i-0bc2fbfadd2aec25b
echo Region: eu-north-1 (Stockholm)
echo.
echo After connecting, run the setup commands manually
echo (See: setup_server_commands.txt)
echo.
pause

ssh -i "C:\Users\tarik\Desktop\meeee.pem" ubuntu@ec2-51-21-221-202.eu-north-1.compute.amazonaws.com
