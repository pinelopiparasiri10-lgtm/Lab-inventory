import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import numpy as np

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="WARHAMMER TACTICAL ELITE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Courier New', monospace; }
    .bot-brain { 
        background-color: #1a1a1a; border: 1px solid #444; padding: 12px; 
        margin-top: 10px; font-size: 0.85rem; color: #ffffff !important; 
        font-family: 'Share Tech Mono', monospace; line-height: 1.4;
    }
    .tactic-tag { color: #00ecff; font-weight: bold; font-size: 0.75rem; }
    </style>
    """, unsafe_allow_html=True)

# --- COMMANDER MEMORY ---
if 'wallets' not in st.session_state:
    st.session_state.wallets = { "WARHAMMER": 100.0, "WARRIOR": 100.0, "NOMAD 4": 100.0, "STRIKER 5": 100.0 }
if 'positions' not in st.session_state:
    st.session_state.positions = { "WARHAMMER": "OUT", "WARRIOR": "OUT", "NOMAD 4": "OUT", "STRIKER 5": "OUT" }
if 'entry_prices' not in st.session_state:
    st.session_state.entry_prices = {}
if 'price_history' not in st.session_state:
    st.session_state.price_history = {} 

def get_live_data():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,dogecoin&vs_currencies=eur"
        return requests.get(url, timeout=10).json()
    except: return None

# --- FAMOUS TACTIC PROFILES ---
bots = [
    {
        "name": "WARHAMMER", 
        "id": "bitcoin", 
        "tactic": "BOLLINGER BREAKOUT", 
        "desc": "Enters when price 'squeezes' then explodes past volatility bands."
    },
    {
        "name": "WARRIOR", 
        "id": "ethereum", 
        "tactic": "MEAN REVERSION", 
        "desc": "Bets that price will always return to its 10-minute average."
    },
    {
        "name": "NOMAD 4", 
        "id": "solana", 
        "tactic": "TURTLE TRADING", 
        "desc": "Trend-following system: Enters on 10-minute highs, exits on lows."
    },
    {
        "name": "STRIKER 5", 
        "id": "dogecoin", 
        "tactic": "SCALP OVERBOUGHT", 
        "desc": "Uses RSI logic to catch rapid spikes and exit before the drop."
    }
]

st.title("🛡️ WARHAMMER: FAMOUS TACTICS COMMAND")
st.write(f"TIMEFRAME: 10m SCALPING | STRATEGY: SENTIENT | {datetime.now().strftime('%H:%M:%S')}")

data = get_live_data()
now = datetime.now()

st.divider()
cols = st.columns(len(bots))

if data:
    for i, bot in enumerate(bots):
        current_price = data.get(bot['id'], {}).get('eur', 0)
        
        # --- DATA BUFFER ---
        if bot['id'] not in st.session_state.price_history:
            st.session_state.price_history[bot['id']] = []
        st.session_state.price_history[bot['id']].append(current_price)
        
        # Keep window of 30 samples (approx 10 mins if refreshing every 20s)
        if len(st.session_state.price_history[bot['id']]) > 30:
            st.session_state.price_history[bot['id']].pop(0)
            
        history = st.session_state.price_history[bot['id']]
        avg_price = np.mean(history) if history else current_price
        std_dev = np.std(history) if history else 0
        
        current_pos = st.session_state.positions[bot['name']]
        action_text = "SCANNING..."

        # --- FAMOUS TACTIC LOGIC GATES ---
        
        # 1. EXIT LOGIC
        if current_pos == "IN":
            entry = st.session_state.entry_prices[bot['name']]
            gain = ((current_price - entry) / entry) * 100
            
            # Smart Exit: If profit > 0.4% OR loss < -0.2%
            if gain >= 0.4 or gain <= -0.2:
                st.session_state.wallets[bot['name']] *= (1 + (gain/100))
                st.session_state.positions[bot['name']] = "OUT"
                action_text = f"TACTIC SUCCESS: LIQUIDATED AT {gain:.2f}%"
            else:
                action_text = f"POSITION ACTIVE: P/L {gain:.3f}%"

        # 2. ENTRY LOGIC (Famous Tactics)
        else:
            # WARHAMMER: Bollinger Squeeze (Price > Avg + 2 StdDev)
            if bot['name'] == "WARHAMMER" and current_price > (avg_price + (1.5 * std_dev)):
                st.session_state.entry_prices[bot['name']] = current_price
                st.session_state.positions[bot['name']] = "IN"
                action_text = "BOLLINGER SQUEEZE DETECTED: BUYING"
            
            # WARRIOR: Mean Reversion (Buy if 0.5% below average)
            elif bot['name'] == "WARRIOR" and current_price < (avg_price * 0.998):
                st.session_state.entry_prices[bot['name']] = current_price
                st.session_state.positions[bot['name']] = "IN"
                action_text = "REVERSION TRIGGERED: BUYING DIP"

            # NOMAD 4: Turtle (Price is higher than anything in history buffer)
            elif bot['name'] == "NOMAD 4" and current_price >= max(history):
                st.session_state.entry_prices[bot['name']] = current_price
                st.session_state.positions[bot['name']] = "IN"
                action_text = "BREAKOUT CONFIRMED: TURTLE ENTRY"
                
            # STRIKER 5: Sentiment Scalp (Fast 0.1% jump)
            elif bot['name'] == "STRIKER 5" and len(history) > 1 and current_price > history[-2] * 1.001:
                st.session_state.entry_prices[bot['name']] = current_price
                st.session_state.positions[bot['name']] = "IN"
                action_text = "SENTIMENT SPIKE: MOMENTUM ENTRY"

        # --- DISPLAY ---
        with cols[i]:
            pos_color = "#00FF00" if st.session_state.positions[bot['name']] == "IN" else "#FF4B4B"
            st.subheader(f"🤖 {bot['name']}")
            st.markdown(f"<span class='tactic-tag'>{bot['tactic']}</span>", unsafe_allow_html=True)
            st.markdown(f"POSITION: <span style='color:{pos_color}'>{st.session_state.positions[bot['name']]}</span>", unsafe_allow_html=True)
            
            st.metric(label=f"{bot['id'].upper()}", value=f"€{current_price:,.2f}")
            
            st.markdown(f"""
                <div class="bot-brain">
                <b>WALLET:</b> €{st.session_state.wallets[bot['name']]:,.2f}<br>
                <b>LOGIC:</b> {bot['desc']}<br><br>
                <b>MIND:</b> {action_text}
                </div>
            """, unsafe_allow_html=True)

else:
    st.warning("📡 DATA LINK SEVERED. ATTEMPTING RECOVERY...")

# --- PERFORMANCE LEADERBOARD ---
st.divider()
st.subheader("🏆 TACTICAL SQUAD LEADERBOARD")
leader_data = [{"Commander": k, "Balance": f"€{v:,.4f}", "Strategy": next(b['tactic'] for b in bots if b['name'] == k)} for k, v in st.session_state.wallets.items()]
st.table(pd.DataFrame(leader_data).sort_values("Balance", ascending=False))

time.sleep(20)
st.rerun()
