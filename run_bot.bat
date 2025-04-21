
@echo off
cls
echo =======================================
echo     Solana Meme Coin Trading Bot
echo =======================================

:: Prompt user for their base64 private key
set /p PHANTOM_PRIVATE_KEY=Paste your Phantom private key (base64): 

:: Install required Python modules (only first time)
pip install requests flask solders solana >nul 2>&1

:: Run the bot
python app.py

pause