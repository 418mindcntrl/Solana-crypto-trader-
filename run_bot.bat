@echo off
cls
echo ===============================
echo  Starting Solana Trading Bot...
echo ===============================

:: Install dependencies if missing
pip install requests flask solders solana

:: Set your private key here
set PHANTOM_PRIVATE_KEY=PASTE_YOUR_KEY_HERE

:: Run the bot
python app.py

pause
