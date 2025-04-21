
@echo off
cls
echo =======================================
echo     Solana Meme Coin Trading Bot
echo =======================================

:: Prompt user for their base64/base58/JSON private key
set /p PHANTOM_PRIVATE_KEY=Paste your Phantom private key (base64/base58/JSON): 

:: Optional: install required dependencies
echo Installing dependencies...
pip install -r requirements.txt >nul 2>&1

:: Run the bot
echo Starting bot...
set PHANTOM_PRIVATE_KEY=%PHANTOM_PRIVATE_KEY%
python app.py

pause