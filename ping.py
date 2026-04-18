import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- SYSTEM CONFIG & STYLING ---
st.set_page_config(page_title="WARHAMMER TACTICAL NETWORK", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    /* White Text for Labels and Minds */
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-weight: bold; font-size: 1.1rem; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Courier New', monospace; }
    .bot-brain { 
        background-color: #1a1a1a; 
        border: 1px solid #444; 
        padding: 12px; 
        margin-top: 10px; 
        font-size: 0.9rem; 
        color: #ffffff !important;  /* Forced White Text */
        font-family: 'Share Tech Mono', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

def get_market_data():
    try:
        # Fetching price and 24h change
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,dogecoin&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

# --- SMART BOT STRATEGIES ---
# Profiles define how they react to the percentage change
bots = [
    {
        "name": "WARHAMMER", 
        "asset_id": "bitcoin", 
        "display": "BITCOIN", 
        "logic": "Aggressive Arbitrage",
        "thought": "High volume detected. Pushing for maximum leverage. Ignoring standard resistance levels."
    },
    {
        "name": "WARRIOR", 
        "asset_id": "ethereum", 
        "display": "ETHEREUM", 
        "logic": "Adaptive Scalping",
        "thought": "Network activity rising. Entering micro-positions. Harvesting 0.5% swings continuously."
    },
    {
        "name": "NOMAD 4", 
        "asset_id": "solana", 
        "display": "SOLANA", 
        "logic": "Volatility Hunter",
        "thought": "Speed is life. Monitoring TPS count. Will liquidate if momentum slows by 2%."
    },
    {
        "name": "STRIKER 5", 
        "asset_id": "dogecoin", 
        "display": "DOGECOIN", 
        "logic": "Sentiment Analysis",
        "thought": "Social signal spike detected. Following the crowd. Stop-loss set tight at -4%."
    }
]

# --- MAIN INTERFACE ---
st.title("🛡️ WARHAMMER TACTICAL NETWORK")
st.write(f"SQUAD STATUS: UNLEASHED | SCAN: {datetime.now().strftime('%H:%M:%S')}")

data = get_market_data()
st.divider()

# --- TOP ROW: BOT COMMANDERS ---
cols = st.columns(len(bots))

if data:
    for i, bot in enumerate(bots):
        asset_data = data.get(bot['asset_id'], {})
        price = asset_data.get('usd', 0)
        change_24h = asset_data.get('usd_24h_change', 0)
        
        # SMART LOGIC: Only stops if it hits the bottom (Safety Switch)
        is_active = True
        if change_24h < -10.0:  # Absolute safety floor to prevent total loss
            is_active = False

        with cols[i]:
            st.subheader(f"🤖 {bot['name']}")
            
            if is_active:
                st.metric(label=bot['display'], value=f"${price:,.2f}", delta=f"{change_24h:.2f}%")
                
                # THE WHITE "MIND" INTERFACE
                st.markdown(f"""
                <div class="bot-brain">
                <b>TACTIC:</b> {bot['logic']}<br><br>
                <b>MINDSET:</b> {bot['thought']}<br><br>
                <b>STATUS:</b> SEARCHING FOR ENTRY
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"NODE {bot['name']} SHUTDOWN: MARKET CRASH")
                st.metric(label=bot['display'], value=f"${price:,.2f}", delta=f"{change_24h:.2f}%")

else:
    st.warning("⚠️ CONNECTION INTERRUPTED: CHECKING SATELLITE LINK...")

st.divider()

# --- LEADERBOARD ---
st.subheader("🏆 SQUAD LEADERBOARD")
leader_list = []
for b in bots:
    ch = data.get(b['asset_id'], {}).get('usd_24h_change', 0) if data else 0
    leader_list.append({
        "Bot": b['name'], 
        "Strategy": b['logic'], 
        "Target": b['display'], 
        "Current ROI %": round(ch, 2)
    })

df = pd.DataFrame(leader_list).sort_values(by="Current ROI %", ascending=False)
st.table(df)

# System Log
st.code(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALL LIMITS REMOVED. BOTS ARE OPERATING ON INDEPENDENT LOGIC.")

time.sleep(60)
st.rerun()
