@echo off
cls
echo ===============================
echo  Starting Solana Trading Bot...
echo ===============================

:: Make sure Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

:: Set your private key here
set PHANTOM_PRIVATE_KEY=PASTE_YOUR_BASE64_KEY_HERE

:: Run the bot
python app.py

:: Wait for user to press a key
pause
