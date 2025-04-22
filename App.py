import os
import time
import threading
import requests
import json
import base64
from base58 import b58decode
from flask import Flask, render_template_string, redirect
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.types import TxOpts

# Prompt user for Phantom private key
print("Paste your Phantom private key (Base64 / Base58 / JSON):")
key_raw = input("> ").strip()

def load_wallet(key_input: str) -> Keypair:
    try:
        key = base64.b64decode(key_input)
        print("[INFO] Loaded Base64 key")
        return Keypair.from_secret_key(key)
    except:
        pass
    try:
        key = b58decode(key_input)
        print("[INFO] Loaded Base58 key")
        return Keypair.from_secret_key(key)
    except:
        pass
    try:
        key = bytes(json.loads(key_input))
        print("[INFO] Loaded JSON array key")
        return Keypair.from_secret_key(key)
    except:
        pass
    raise ValueError("Invalid private key format.")

wallet = load_wallet(key_raw)
public_key = wallet.public_key
print("\n[WALLET LOADED]")
print("Public Key:", public_key)

client = Client("https://api.mainnet-beta.solana.com")
try:
    balance_sol = client.get_balance(public_key)["result"]["value"] / 1e9
    print("Balance:", balance_sol, "SOL\n")
except Exception as e:
    print("[ERROR] Could not fetch balance:", e)

# Constants and Flask app setup
SLIPPAGE = 1
PROFIT_TARGET = 1.5
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
TRADING_ENABLED = False
state = {"price": 0.0, "buy_price": None, "holding": False}
logs = []
app = Flask(__name__)

def log(msg):
    timestamp = time.strftime("[%H:%M:%S]")
    logs.insert(0, f"{timestamp} {msg}")
    logs[:] = logs[:100]

def get_price():
    try:
        res = requests.get("https://quote-api.jup.ag/v6/quote", params={
            "inputMint": SOL_MINT,
            "outputMint": USDC_MINT,
            "amount": int(1e9)
        })
        data = res.json()
        return int(data["data"]["outAmount"]) / 1e6 if "data" in data and "outAmount" in data["data"] else 0.0
    except Exception as e:
        log(f"[PRICE ERROR] {e}")
        return 0.0

def get_sol_balance():
    try:
        res = client.get_balance(public_key)
        return res["result"]["value"] / 1e9
    except Exception as e:
        print("[ERROR] Could not get SOL balance:", e)
        return 0.0

def swap(input_mint, output_mint, amount=None):
    try:
        quote = requests.post("https://quote-api.jup.ag/v6/swap", json={
            "userPublicKey": str(public_key),
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount) if amount else None,
            "slippageBps": str(SLIPPAGE * 100),
            "swapMode": "ExactIn"
        }).json()
        tx_bytes = base64.b64decode(quote["swapTransaction"])
        tx = Transaction.deserialize(tx_bytes)
        tx.sign(wallet)
        client.send_transaction(tx, wallet, opts=TxOpts(skip_preflight=True))
        log(f"[TX] Swap: {input_mint[:4]} â {output_mint[:4]}")
        return True
    except Exception as e:
        log(f"[ERROR] Swap failed: {e}")
        return False

def trade_loop():
    global TRADING_ENABLED
    while True:
        if TRADING_ENABLED:
            price = get_price()
            state["price"] = price
            if not state["holding"]:
                sol = get_sol_balance()
                spend = max(0, sol - 0.002)
                log(f"[CHECK] SOL balance: {sol}, Spendable: {spend}")
                if spend >= 0.001:
                    log(f"[ATTEMPT] Swapping {spend} SOL â USDC...")
                    if swap(SOL_MINT, USDC_MINT, int(spend * 1e9)):
                        state["buy_price"] = price
                        state["holding"] = True
                        log(f"[BUY] USDC @ {price}")
                    else:
                        log("[SWAP FAIL] Could not buy USDC")
        time.sleep(30)

@app.route("/", methods=["GET"])
def dashboard():
    toggle_label = "Pause Bot" if TRADING_ENABLED else "Start Bot"
    return render_template_string("""
    <html><head><title>SOL-USDC Trader</title></head>
    <body style="background:#0d1117;color:#c9d1d9;font-family:sans-serif;padding:20px;">
    <h2>SOL â USDC Auto-Trader</h2>
    <p><b>Wallet:</b> {{ pub }}</p>
    <form action="/toggle" method="post">
        <button type="submit" style="padding:8px 16px;">{{ toggle_label }}</button>
    </form>
    <h3>Status:</h3>
    <div>USDC Price (1 SOL): {{ price }}</div>
    <div>Holding USDC: {{ holding }}</div>
    {% if buy_price %}
        <div>Bought @: {{ buy_price }}</div>
    {% endif %}
    <h3>Logs:</h3>
    <pre>{% for l in logs %}{{ l }}\n{% endfor %}</pre>
    </body></html>
    """, logs=logs, pub=public_key, price=state["price"], holding=state["holding"], buy_price=state["buy_price"])

@app.route("/toggle", methods=["POST"])
def toggle():
    global TRADING_ENABLED
    TRADING_ENABLED = not TRADING_ENABLED
    log(f"Trading {'ENABLED' if TRADING_ENABLED else 'PAUSED'} by user")
    return redirect("/")

if __name__ == "__main__":
    threading.Thread(target=trade_loop).start()
    app.run(host="0.0.0.0", port=5000)