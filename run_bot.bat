@echo off
cls
echo =======================================
echo   Solana Meme Coin Auto-Trading Bot
echo =======================================

pip install -r requirements.txt >nul 2>&1

python app.py

pause