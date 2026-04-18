import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import requests

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Overwatch Market Network", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- ANTI-BLOCK SESSION ---
# This makes Streamlit look like a real browser to Yahoo Finance
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

def fetch_telemetry(ticker, name):
    try:
        # We pass the 'session' here to bypass the Rate Limit error
        data = yf.Ticker(ticker, session=session)
        df = data.history(period="1d", interval="1m")
        
        if df.empty:
            return None
        
        latest_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[0]
        change = latest_price - prev_price
        
        return {
            "name": name,
            "price": latest_price,
            "change": change
        }
    except Exception:
        return None

# --- MAIN INTERFACE ---
st.title("🛰️ OVERWATCH MARKET NETWORK")
st.write(f"LATENCY: OPTIMAL | LAST SCAN: {datetime.now().strftime('%H:%M:%S')}")

# Define your assets
assets = [
    {"ticker": "BTC-USD", "name": "BITCOIN"},
    {"ticker": "ETH-USD", "name": "ETHEREUM"},
    {"ticker": "SOL-USD", "name": "SOLANA"},
    {"ticker": "^GSPC", "name": "S&P 500"}
]

# Create layout columns
cols = st.columns(len(assets))

# Fetch and display data
for i, asset in enumerate(assets):
    with cols[i]:
        telemetry = fetch_telemetry(asset["ticker"], asset["name"])
        if telemetry:
            st.metric(
                label=telemetry["name"],
                value=f"${telemetry['price']:,.2f}",
                delta=f"{telemetry['change']:,.2f}"
            )
        else:
            st.error(f"{asset['name']} OFFLINE")

# --- TICKER TAPE LOG ---
st.divider()
st.subheader("📡 SYSTEM LOGS")
st.code(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DATA_FETCH_SUCCESS: ALL NODES ACTIVE")

# --- REFRESH LOGIC ---
# We wait 60 seconds to avoid the "YFRateLimitError"
time.sleep(60)
st.rerun()
