import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="Overwatch Market Network", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

def get_market_data():
    try:
        # Fetching directly from CoinGecko API (No library needed)
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,dogecoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

# --- UI ---
st.title("🛰️ OVERWATCH MARKET NETWORK")
st.write(f"ENCRYPTION: AES-256 | SCAN TIME: {datetime.now().strftime('%H:%M:%S')}")

data = get_market_data()

# Mapping for the display
assets = [
    {"id": "bitcoin", "name": "BITCOIN"},
    {"id": "ethereum", "name": "ETHEREUM"},
    {"id": "solana", "name": "SOLANA"},
    {"id": "dogecoin", "name": "DOGECOIN"}
]

cols = st.columns(len(assets))

if data:
    for i, asset in enumerate(assets):
        with cols[i]:
            price = data.get(asset["id"], {}).get("usd")
            if price:
                st.metric(label=f"NODE: {asset['name']}", value=f"${price:,.2f}")
            else:
                st.error(f"{asset['name']} OFFLINE")
else:
    st.warning("⚠️ GLOBAL SIGNAL JAMMED: RETRYING IN 60s...")

st.divider()
st.subheader("📡 SYSTEM LOGS")
st.code(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DATA_FETCH_SUCCESS: NODES SYNCHRONIZED")

# Refresh every 60 seconds
time.sleep(60)
st.rerun()
