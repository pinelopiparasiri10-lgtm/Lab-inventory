import streamlit as st
import cryptocompare
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Overwatch Market Network", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FETCHING ---
def get_crypto_data(coin):
    try:
        # Fetch price in USD
        price_data = cryptocompare.get_price(coin, curr='USD')
        if price_data:
            return price_data[coin]['USD']
        return None
    except:
        return None

# --- MAIN INTERFACE ---
st.title("🛰️ OVERWATCH MARKET NETWORK")
st.write(f"SYSTEM STATUS: ACTIVE | SCAN TIME: {datetime.now().strftime('%H:%M:%S')}")

# List of assets to track
coins = ["BTC", "ETH", "SOL", "DOGE"]
cols = st.columns(len(coins))

for i, coin in enumerate(coins):
    with cols[i]:
        price = get_crypto_data(coin)
        if price:
            st.metric(label=f"NODE: {coin}", value=f"${price:,.2f}")
        else:
            st.error(f"{coin} SIGNAL LOST")

st.divider()
st.subheader("📡 LIVE TELEMETRY")
st.code(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DATA_LINK_ESTABLISHED")

# Refresh every 30 seconds
time.sleep(30)
st.rerun()
