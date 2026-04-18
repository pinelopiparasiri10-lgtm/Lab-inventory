import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="WARHAMMER TACTICAL NETWORK", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Courier New', monospace; }
    .bot-brain { background-color: #0e1117; border-left: 5px solid #ff4b4b; padding: 10px; margin-top: 5px; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

def get_market_data():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,dogecoin&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

# --- BOT CONFIGURATION ---
bots = [
    {"name": "WARHAMMER", "asset_id": "bitcoin", "display": "BITCOIN", "strategy": "AGGRESSIVE", "stop_loss": -2.0},
    {"name": "WARRIOR", "asset_id": "ethereum", "display": "ETHEREUM", "strategy": "SCALPING", "stop_loss": -1.5},
    {"name": "NOMAD 4", "asset_id": "solana", "display": "SOLANA", "strategy": "TREND FOLLOW", "stop_loss": -3.0},
    {"name": "STRIKER 5", "asset_id": "dogecoin", "display": "DOGECOIN", "strategy": "MOMENTUM", "stop_loss": -5.0}
]

st.title("🛰️ WARHAMMER TACTICAL NETWORK")
st.write(f"SQUAD STATUS: OPERATIONAL | SCAN: {datetime.now().strftime('%H:%M:%S')}")

data = get_market_data()
st.divider()

# --- TOP ROW: BOT COMMANDERS & ASSETS ---
cols = st.columns(len(bots))

if data:
    for i, bot in enumerate(bots):
        asset_data = data.get(bot['asset_id'], {})
        price = asset_data.get('usd', 0)
        change_24h = asset_data.get('usd_24h_change', 0)
        
        # LOGIC: EXIT IF PROFIT > 5% OR DROP < STOP_LOSS
        is_active = True
        status_msg = "RUNNING"
        
        if change_24h > 5.0:
            is_active = False
            status_msg = "EXITED (PROFIT TARGET MET)"
        elif change_24h < bot['stop_loss']:
            is_active = False
            status_msg = "EMERGENCY STOP (LOSS LIMIT)"

        with cols[i]:
            # Bot Header
            st.subheader(f"🤖 {bot['name']}")
            st.caption(f"Strategy: {bot['strategy']}")
            
            # Asset Display
            if is_active:
                st.metric(label=bot['display'], value=f"${price:,.2f}", delta=f"{change_24h:.2f}%")
                
                # --- BOT INTERFACE (THE "MIND") ---
                st.markdown(f"""
                <div class="bot-brain">
                <b>THOUGHTS:</b> Detecting volatility. Adjusting for {bot['strategy']} parameters.<br>
                <b>ACTION:</b> HOLDING POSITION / MONITORING.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"NODE OFFLINE: {status_msg}")
                st.metric(label=bot['display'], value=f"${price:,.2f}", delta=f"{change_24h:.2f}%")

else:
    st.warning("SIGNAL JAMMED: RECONNECTING...")

st.divider()

# --- LEADERBOARD ---
st.subheader("🏆 SQUAD PERFORMANCE LEADERBOARD")
leader_list = []
for b in bots:
    ch = data.get(b['asset_id'], {}).get('usd_24h_change', 0) if data else 0
    leader_list.append({"Bot": b['name'], "Tactical Asset": b['display'], "Current Yield %": round(ch, 2)})

df = pd.DataFrame(leader_list).sort_values(by="Current Yield %", ascending=False)
st.table(df)

# System Log
st.code(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOG: {len(bots)} bots scanning markets. Safety triggers armed.")

time.sleep(60)
st.rerun()
