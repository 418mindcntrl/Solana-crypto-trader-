@echo off
cls
echo =======================================
echo   Solana Meme Coin Auto-Trading Bot
echo =======================================

:: Prompt user for their key
set /p USER_KEY=Paste your Phantom private key (Base64/Base58/JSON): 

:: Write the key into a temporary environment file
echo set PHANTOM_PRIVATE_KEY=%USER_KEY% > env.bat

:: Load the key
call env.bat

:: Install required dependencies
pip install -r requirements.txt >nul 2>&1

:: Start the bot
python app.py

pause