


import os
import time
import threading
import requests
import json
import base64
from base58 import b58decode
from flask import Flask, request, render_template_string, redirect
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.types import TxOpts

# ===== Prompt for Private Key =====
print("Paste your Phantom private key (Base64 / Base58 / JSON):")
key_raw = input("> ").strip()

def load_wallet(key_input: str) -> Keypair:
    try: return Keypair.from_secret_key(base64.b64decode(key_input))
    except: pass
    try: return Keypair.from_secret_key(b58decode(key_input))
    except: pass
    try: return Keypair.from_secret_key(bytes(json.loads(key_input)))
    except: pass
    raise ValueError("Invalid private key format.")

wallet = load_wallet(key_raw)
public_key = str(wallet.public_key)
client = Client("https://api.mainnet-beta.solana.com")

SLIPPAGE = 1
PROFIT_TARGET = 1.5
SOL_MINT = "So11111111111111111111111111111111111111112"
TRADING_ENABLED = False

TOKENS = [
    {"symbol": "WIF", "mint": "5dAPUcB5kDo61tJmoMscJZo8vnkfLDKo3XBqDKt8WZz7", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "JUP", "mint": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "USDC", "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "price": 0.0, "buy_price": None, "holding": False},
    {"symbol": "PYTH", "mint": "PYTHnPvHyduF6C6CJwjjcRh7xnWwGEEpB2CSDBVXc4C", "price": 0.0, "buy_price": None, "holding": False}
]

app = Flask(__name__)
logs = []

def log(msg):
    timestamp = time.strftime("[%H:%M:%S]")
    logs.insert(0, f"{timestamp} {msg}")
    logs[:] = logs[:100]

def get_price(mint):
    try:
        # 1 SOL in lamports
        amount = int(1e9)
        res = requests.get(
            "https://quote-api.jup.ag/v6/quote",
            params={
                "inputMint": SOL_MINT,
                "outputMint": mint,
                "amount": amount
            }
        )
        data = res.json()
        out_amount = int(data["data"][0]["outAmount"])
        price = out_amount / 1e9
        return round(price, 10)
    except Exception as e:
        log(f"[PRICE ERROR] {mint[:4]}: {e}")
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
    global TRADING_ENABLED
    while True:
        if TRADING_ENABLED:
            for token in TOKENS:
                token["price"] = get_price(token["mint"])
                if token["price"] == 0:
                    continue
                if not token["holding"]:
                    sol = get_sol_balance()
                    spend = max(0, sol - 0.002)
                    if spend >= 0.001:
                        if swap(SOL_MINT, token["mint"], int(spend * 1e9)):
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
    toggle_label = "Pause Bot" if TRADING_ENABLED else "Start Bot"
    return render_template_string("""
    <html><head><title>Solana Bot</title></head>
    <body style="background:#0d1117;color:#c9d1d9;font-family:sans-serif;padding:20px;">
    <h2>Solana Auto-Trader</h2>
    <p><b>Wallet:</b> {{ pub }}</p>
    <form action="/toggle" method="post">
        <button type="submit" style="padding:8px 16px;">{{ toggle_label }}</button>
    </form>
    <h3>Status:</h3>
    {% for token in tokens %}
        <div>{{ token.symbol }} | Price: {{ token.price }} | Holding: {{ token.holding }}{% if token.buy_price %} (Bought @ {{ token.buy_price }}){% endif %}</div>
    {% endfor %}
    <h3>Logs:</h3>
    <pre>{% for l in logs %}{{ l }}\n{% endfor %}</pre>
    </body></html>
    """, logs=logs, tokens=TOKENS, pub=public_key, toggle_label=toggle_label)

@app.route("/toggle", methods=["POST"])
def toggle():
    global TRADING_ENABLED
    TRADING_ENABLED = not TRADING_ENABLED
    log(f"Trading {'ENABLED' if TRADING_ENABLED else 'PAUSED'} by user")
    return redirect("/")

if __name__ == "__main__":
    threading.Thread(target=trade_loop).start()
    app.run(host="0.0.0.0", port=5000)