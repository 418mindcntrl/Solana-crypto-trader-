@echo off
cls
echo =======================================
echo   Solana Meme Coin Auto-Trading Bot
echo =======================================

:: Install required packages if needed
pip install -r requirements.txt >nul 2>&1

:: Create temporary script with private key prompt
echo print("Paste your Phantom private key (Base64 / Base58 / JSON):") > temp_launch.py
echo key_raw = input("> ").strip() >> temp_launch.py
type app.py >> temp_launch.py

:: Run the bot
python temp_launch.py

:: Cleanup
del temp_launch.py

pause