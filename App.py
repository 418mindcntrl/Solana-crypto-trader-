import os
import time
import threading
import requests
import json
import base64
from base58 import b58decode
from flask import Flask, render_template_string
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.publickey import PublicKey

# ===== User Authentication =====
print("Welcome to Solana Meme Coin Auto-Trader")
username = input("Enter username: ").strip()
password = input("Enter password: ").strip()

if username != "admin" or password != "1234":
    print("Access denied.")
    exit()

# ===== Private Key Input =====
print("Paste your Phantom private key (Base64 / Base58 / JSON):")
key_raw = input("> ").strip()

# ===== Key Loader =====
def load_wallet(key_input: str) -> Keypair:
    try:
        return Keypair.from_secret_key(base64.b64decode(key_input))
    except: pass
    try:
        return Keypair.from_secret_key(b58decode(key_input))
    except: pass
    try:
        if key_input.startswith("["):
            return Keypair.from_secret_key(bytes(json.loads(key_input)))
    except: pass
    raise ValueError("Invalid key format. Use base64, base58, or JSON.")

wallet = load_wallet(key_raw)
del key_raw
public_key = str(wallet.public_key)
client = Client("https://api.mainnet-beta.solana.com")

# ===== Bot Config =====
SLIPPAGE = 1
PROFIT_TARGET = 1.5
SOL_MINT = "So11111111111111111111111111111111111111112"

TOKENS = [
    {"symbol": "BONK", "mint": "DezXQyF1i2nYzVKjLFh9jq5EujnhPiyx4TKY4LzsdLoL", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "WIF", "mint": "5G6RxWyyMFD1Zz3De5QnUvo8WQ3CUEU6dE2S9ZcRZb5i", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "JUP", "mint": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "SLERF", "mint": "SLERFNUA1NdFZjcDhZzB5tPoXz5FtJ4HYjGQqtF4hhR", "price": 0.0, "buy_price": None, "holding": False}
]

# ===== Flask Dashboard =====
app = Flask(__name__)
logs = []

def log(msg):
    timestamp = time.strftime("[%H:%M:%S]")
    logs.insert(0, f"{timestamp} {msg}")
    logs[:] = logs[:100]

def get_price(symbol):
    try:
        res = requests.get(f"https://price.jup.ag/v4/price?ids={symbol}")
        return float(res.json()["data"][symbol]["price"])
    except:
        return 0.0

def get_sol_balance():
    try:
        res = client.get_balance(wallet.public_key)
        return res['result']['value'] / 1e9
    except:
        return 0.0

def swap(input_mint, output_mint, amount=None):
    try:
        quote = requests.post("https://quote-api.jup.ag/v6/swap", json={
            "userPublicKey": public_key,
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount) if amount else None,
            "slippageBps": str(SLIPPAGE * 100),
            "swapMode": "ExactIn" if amount else "ExactOut"
        }).json()

        from solana.transaction import Transaction
        from solana.rpc.types import TxOpts
        tx_bytes = base64.b64decode(quote["swapTransaction"])
        tx = Transaction.deserialize(tx_bytes)
        tx.sign(wallet)
        client.send_transaction(tx, wallet, opts=TxOpts(skip_preflight=True))
        log(f"[TX] Swap: {input_mint[:4]} → {output_mint[:4]}")
        return True
    except Exception as e:
        log(f"[ERROR] Swap failed: {e}")
        return False

def trade_loop():
    while True:
        for token in TOKENS:
            token["price"] = get_price(token["symbol"])
            if token["price"] == 0:
                continue
            if not token["holding"]:
                available_sol = get_sol_balance()
                spend_amount = max(0, available_sol - 0.002)  # leave a little for fees
                if spend_amount >= 0.001:
                    if swap(SOL_MINT, token["mint"], int(spend_amount * 1e9)):
                        token["buy_price"] = token["price"]
                        token["holding"] = True
                        log(f"[BUY] {token['symbol']} @ {token['price']}")
            elif token["price"] >= token["buy_price"] * PROFIT_TARGET:
                if swap(token["mint"], SOL_MINT):
                    token["holding"] = False
                    log(f"[SELL] {token['symbol']} @ {token['price']}")
        time.sleep(30)

@app.route("/", methods=["GET"])
def dashboard():
    return render_template_string("""
    <html><head><title>Solana Bot</title></head><body style="background:#0d1117;color:#c9d1d9;font-family:sans-serif;padding:20px;">
    <h2>Solana Auto-Trader</h2>
    <p><b>Wallet:</b> {{ pub }}</p>
    <h3>Status:</h3>
    {% for token in tokens %}
    <div>{{ token.symbol }} | Price: {{ token.price }} | Holding: {{ token.holding }}{% if token.buy_price %} (Bought @ {{ token.buy_price }}){% endif %}</div>
    {% endfor %}
    <h3>Logs:</h3>
    <pre>{% for l in logs %}{{ l }}
{% endfor %}</pre>
    </body></html>
    """, logs=logs, tokens=TOKENS, pub=public_key)

if __name__ == "__main__":
    threading.Thread(target=trade_loop).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))