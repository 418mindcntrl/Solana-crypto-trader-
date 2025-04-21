# Solana Crypto Auto-Trading Bot

This is a plug-and-play, AI-assisted Solana meme coin trading bot powered by Jupiter Aggregator. It trades BONK, WIF, JUP, and SLERF automatically and includes a live dashboard for real-time tracking.

## Features
- Auto-buys top Solana meme coins (BONK, WIF, JUP, SLERF)
- Buys with 0.025 SOL each
- Sells automatically at 1.5× profit
- Jupiter-powered live token pricing
- Secure Phantom wallet integration
- Password-protected web dashboard (Flask)
- 1-click deploy to Render (Free Hosting)

## Live Dashboard (Private)
Once deployed, access your dashboard at:

https://your-app-name.onrender.com

Login credentials (default):
- Username: admin
- Password: solbot2025

> You can change these in `app.py`

## 1-Click Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/418mindcntrl/Solana-crypto-trader-.git)


## Setup Instructions

### 1. Set Your Wallet
You must provide your own Phantom wallet key to activate the bot.

- Generate or export your Phantom private key as a 64-byte Base64 string
- In Render, set this environment variable:

PHANTOM_PRIVATE_KEY=your_base64_key_here

> Use a burner wallet for safety



---

### Option B: Run Locally on Windows

1. Install **Python 3.10+** from [https://python.org](https://python.org)
2. Download or clone this repository
3. Double-click the `run_bot.bat` file
4. When prompted, **paste your base64-encoded Phantom private key**
5. The bot will automatically:
- Install required dependencies (requests, flask, solana, solders)
- Start the trading engine
- Open a live dashboard if included

---

### Don’t Have Your Phantom Private Key?

- Open Phantom Wallet
- Go to Settings → Export Private Key
- Use a burner wallet and convert the key to **64-byte base64**
- Paste it into the terminal when prompted

---





### 2. Fund Your Wallet
After deployment, fund the wallet with ~0.3 SOL to allow trading.

## Tech Stack
- Python (3.10+)
- Flask
- Solana-py + Solders
- Jupiter Aggregator API
- Hosted on Render (Free tier supported)

## Security
- No private key is stored in this repo
- You must provide your own key as an environment variable
- The system is designed for burner wallet usage

## License
MIT — Free for personal or commercial use.

## Questions?
Open an issue or contact the author for customization, additional tokens, or advanced upgrades like Telegram alerts, portfolio logging, or real-time analytics.
