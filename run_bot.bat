@echo off
cls
echo =======================================
echo   Solana Meme Coin Auto-Trading Bot
echo =======================================

:: Install required dependencies
pip install -r requirements.txt >nul 2>&1

:: Run the bot - app.py will prompt for username, password, and private key
python app.py

pause