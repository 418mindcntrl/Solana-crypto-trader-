import time
import threading
import requests
from flask import Flask, render_template_string, request, redirect, url_for
from solders.keypair import Keypair
from solders.transaction import Transaction
from solana.rpc.api import Client
import os
import base64

# === Wallet from ENV ===
key_b64 = os.getenv("PHANTOM_PRIVATE_KEY")
if not key_b64:
    raise ValueError("PHANTOM_PRIVATE_KEY environment variable is required.")
wallet = Keypair.from_bytes(base64.b64decode(key_b64))

# === Flask App with Auth ===
app = Flask(__name__)
logs = []
SLIPPAGE = 1
SPEND_SOL = 0.025
PROFIT_TARGET = 1.5
SOL_MINT = "So11111111111111111111111111111111111111112"

TOKENS = [
    {"symbol": "BONK", "mint": "DezXQyF1i2nYzVKjLFh9jq5EujnhPiyx4TKY4LzsdLoL", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "WIF", "mint": "5G6RxWyyMFD1Zz3De5QnUvo8WQ3CUEU6dE2S9ZcRZb5i", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "JUP", "mint": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "SLERF", "mint": "SLERFNUA1NdFZjcDhZzB5tPoXz5FtJ4HYjGQqtF4hhR", "price": 0.0, "buy_price": None, "holding": False}
]

USERNAME = "admin"
PASSWORD = "solbot2025"

def log(msg):
    logs.insert(0, f"[{time.strftime('%H:%M:%S')}] {msg}")
    logs[:] = logs[:100]

def get_price(symbol):
    try:
        r = requests.get(f"https://price.jup.ag/v4/price?ids={symbol}")
        return float(r.json()["data"][symbol]["price"])
    except Exception as e:
        log(f"[ERROR] Price for {symbol}: {e}")
        return 0.0

def swap(input_mint, output_mint, amount=None):
    try:
        url = "https://quote-api.jup.ag/v6/swap"
        payload = {
            "userPublicKey": str(pubkey),
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount) if amount else None,
            "slippageBps": str(SLIPPAGE * 100),
            "swapMode": "ExactIn" if amount else "ExactOut"
        }
        quote = requests.post(url, json=payload).json()
        tx = Transaction.from_bytes(bytes.fromhex(quote["swapTransaction"]))
        tx.sign([wallet])
        tx_encoded = tx.serialize().hex()
        send = requests.post("https://rpc-proxy.jup.ag/v1/sendTransaction", json={"transaction": tx_encoded}).json()
        sig = send.get("signature", "unknown")
        log(f"[TX] Swap: https://solscan.io/tx/{sig}")
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
                log(f"[BUY] {token['symbol']} @ {token['price']}")
                if swap(SOL_MINT, token["mint"], int(SPEND_SOL * 1e9)):
                    token["buy_price"] = token["price"]
                    token["holding"] = True
            elif token["price"] >= token["buy_price"] * PROFIT_TARGET:
                log(f"[SELL] {token['symbol']} @ {token['price']} (Bought @ {token['buy_price']})")
                if swap(token["mint"], SOL_MINT):
                    token["holding"] = False
                    token["buy_price"] = None
        time.sleep(30)

dashboard_template = """<!DOCTYPE html>
<html><head><title>Bot</title><style>
body { background: #0d1117; color: #c9d1d9; font-family: Arial; padding: 20px; }
.token-box { margin-bottom: 10px; } .log-box { background: #161b22; padding: 10px; border-radius: 8px; max-height: 300px; overflow-y: scroll; }
</style></head><body>
<h1>Solana Auto-Trader Dashboard</h1>
{% for t in tokens %}
<div class="token-box"><strong>{{ t.symbol }}</strong> – Price: ${{ t.price }} – Holding: {{ "YES" if t.holding else "NO" }}{% if t.buy_price %} (Bought @ ${{ t.buy_price }}){% endif %}</div>
{% endfor %}
<h2>Trade Logs</h2><div class="log-box">{% for log in logs %}<div>{{ log }}</div>{% endfor %}</div></body></html>
"""

@app.route("/", methods=["GET", "POST"])
def dashboard():
    auth = request.authorization
    if not auth or auth.username != USERNAME or auth.password != PASSWORD:
        return ('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login"'})
    return render_template_string(dashboard_template, logs=logs, tokens=TOKENS)

if __name__ == "__main__":
    threading.Thread(target=trade_loop).start()
    app.run(host="0.0.0.0", port=10000)
