@echo off
cls
echo =======================================
echo   Solana Meme Coin Auto-Trading Bot
echo =======================================

:: Install required dependencies silently
pip install -r requirements.txt >nul 2>&1

:: Launch the bot (app.py will prompt for the private key)
python app.py

pause