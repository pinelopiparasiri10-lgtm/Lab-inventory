import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import numpy as np

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="WARHAMMER TACTICAL COMMAND", layout="wide")

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
    .total-summary {
        background-color: #0e1117; border: 2px solid #333; padding: 20px;
        border-radius: 10px; text-align: center; margin-top: 20px;
    }
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

bots = [
    {"name": "WARHAMMER", "id": "bitcoin", "tactic": "BOLLINGER BREAKOUT"},
    {"name": "WARRIOR", "id": "ethereum", "tactic": "MEAN REVERSION"},
    {"name": "NOMAD 4", "id": "solana", "tactic": "TURTLE TRADING"},
    {"name": "STRIKER 5", "id": "dogecoin", "tactic": "SENTIMENT SCALP"}
]

st.title("🛡️ WARHAMMER: COMMANDER INTERFACE")
st.write(f"SYSTEM TIME: {datetime.now().strftime('%H:%M:%S')}")

data = get_live_data()
st.divider()

cols = st.columns(len(bots))
total_pl_pct = 0.0

if data:
    for i, bot in enumerate(bots):
        current_price = data.get(bot['id'], {}).get('eur', 0)
        
        # Buffer for math
        if bot['id'] not in st.session_state.price_history:
            st.session_state.price_history[bot['id']] = []
        st.session_state.price_history[bot['id']].append(current_price)
        if len(st.session_state.price_history[bot['id']]) > 30:
            st.session_state.price_history[bot['id']].pop(0)
            
        history = st.session_state.price_history[bot['id']]
        avg_price = np.mean(history) if history else current_price
        std_dev = np.std(history) if history else 0
        
        current_pos = st.session_state.positions[bot['name']]
        live_gain = 0.0
        
        # --- TRADE LOGIC ---
        if current_pos == "IN":
            entry = st.session_state.entry_prices[bot['name']]
            live_gain = ((current_price - entry) / entry) * 100
            total_pl_pct += live_gain # Add to squad total
            
            if live_gain >= 0.45 or live_gain <= -0.25:
                st.session_state.wallets[bot['name']] *= (1 + (live_gain/100))
                st.session_state.positions[bot['name']] = "OUT"
                msg = f"CLOSED: {live_gain:.2f}%"
            else:
                msg = f"TRADE ACTIVE: {live_gain:+.3f}%"
        else:
            # Entry Triggers
            trigger_hit = False
            if bot['name'] == "WARHAMMER" and current_price > (avg_price + (1.5 * std_dev)): trigger_hit = True
            elif bot['name'] == "WARRIOR" and current_price < (avg_price * 0.998): trigger_hit = True
            elif bot['name'] == "NOMAD 4" and current_price >= max(history): trigger_hit = True
            elif bot['name'] == "STRIKER 5" and len(history) > 1 and current_price > history[-2] * 1.001: trigger_hit = True
            
            if trigger_hit:
                st.session_state.entry_prices[bot['name']] = current_price
                st.session_state.positions[bot['name']] = "IN"
                msg = "ENTERING POSITION..."
            else:
                msg = "WAITING FOR SIGNAL"

        with cols[i]:
            color = "#00FF00" if live_gain >= 0 else "#FF4B4B"
            st.subheader(f"🤖 {bot['name']}")
            st.metric(label=f"{bot['id'].upper()}", value=f"€{current_price:,.2f}", delta=f"{live_gain:+.3f}%" if current_pos == "IN" else "IDLE")
            
            st.markdown(f"""
                <div class="bot-brain">
                <b>STRATEGY:</b> {bot['tactic']}<br>
                <b>WALLET:</b> €{st.session_state.wallets[bot['name']]:,.2f}<br>
                <b>MIND:</b> <span style="color:{color if current_pos == 'IN' else '#ffffff'}">{msg}</span>
                </div>
            """, unsafe_allow_html=True)

# --- GLOBAL SUMMARY SECTION ---
st.divider()
total_cash = sum(st.session_state.wallets.values())
initial_total = 400.0
total_growth_pct = ((total_cash - initial_total) / initial_total) * 100

st.markdown(f"""
    <div class="total-summary">
        <h2 style="color:white; margin-bottom:0;">🛰️ GLOBAL SQUAD DISPATCH</h2>
        <div style="display: flex; justify-content: space-around; padding: 20px;">
            <div>
                <p style="color:#888; margin:0;">TOTAL COMMAND BALANCE</p>
                <h1 style="color:#00ecff; margin:0;">€{total_cash:,.2f}</h1>
            </div>
            <div>
                <p style="color:#888; margin:0;">SQUAD PERFORMANCE (NET)</p>
                <h1 style="color:{'#00FF00' if total_growth_pct >= 0 else '#FF4B4B'}; margin:0;">
                    {total_growth_pct:+.4f}%
                </h1>
            </div>
            <div>
                <p style="color:#888; margin:0;">ACTIVE COMBINED P/L</p>
                <h1 style="color:{'#00FF00' if total_pl_pct >= 0 else '#FF4B4B'}; margin:0;">
                    {total_pl_pct:+.3f}%
                </h1>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

time.sleep(20)
st.rerun()
