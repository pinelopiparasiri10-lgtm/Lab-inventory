import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# --- Configuration & High-Contrast Styling ---
st.set_page_config(page_title="Overwatch Market Network", layout="wide")

st.markdown("""
    <style>
    /* Professional Terminal Styling */
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #dcdfe3;
    }
    /* Force Price Text to Black */
    div[data-testid="stMetricValue"] {
        color: #000000 !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        border-radius: 2px;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #000000;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Network and Navigation
if 'page' not in st.session_state:
    st.session_state.page = "main"
if 'network' not in st.session_state:
    st.session_state.network = {
        "Warhammer": {"ticker": "BTC-USD", "label": "BITCOIN", "mode": "Aggressive Scalp", "balance": 100.0, "units": 0, "history": [], "thought": "Initializing surveillance...", "status": "Ready"},
        "Warrior": {"ticker": "ETH-USD", "label": "ETHEREUM", "mode": "Steady Growth", "balance": 100.0, "units": 0, "history": [], "thought": "Initializing surveillance...", "status": "Ready"},
        "Nomad 5": {"ticker": "SOL-USD", "label": "SOLANA", "mode": "Momentum Chase", "balance": 100.0, "units": 0, "history": [], "thought": "Initializing surveillance...", "status": "Ready"},
        "Striker": {"ticker": "DOGE-USD", "label": "DOGECOIN", "mode": "Precision Strike", "balance": 100.0, "units": 0, "history": [], "thought": "Initializing surveillance...", "status": "Ready"}
    }
if 'view_target' not in st.session_state:
    st.session_state.view_target = None

def fetch_telemetry(ticker, mode):
    df = yf.Ticker(ticker).history(period="1d", interval="1m")
    if df.empty: return None
    params = {"Aggressive Scalp": (5, 0.8), "Steady Growth": (15, 1.5), "Momentum Chase": (10, 1.2), "Precision Strike": (30, 2.5)}
    win, dev = params.get(mode, (15, 1.5))
    df['MA'] = df['Close'].rolling(window=win).mean()
    df['Std'] = df['Close'].rolling(window=win).std()
    df['Upper'] = df['MA'] + (df['Std'] * dev)
    df['Lower'] = df['MA'] - (df['Std'] * dev)
    return df

def go_to(page_name, target=None):
    st.session_state.page = page_name
    st.session_state.view_target = target

# --- 1. LEADERBOARD VIEW ---
if st.session_state.page == "leaderboard":
    st.title("📊 Network Rankings")
    leader_data = []
    for name, unit in st.session_state.network.items():
        price = yf.Ticker(unit['ticker']).fast_info['last_price']
        val = unit['balance'] + (unit['units'] * price)
        roi = ((val - 100.0) / 100.0) * 100
        leader_data.append({"Unit": name, "Asset": unit['label'], "ROI %": round(roi, 2), "Equity (€)": round(val, 2)})
    
    st.table(pd.DataFrame(leader_data).sort_values(by="ROI %", ascending=False))
    st.button("Return to Terminal", on_click=go_to, args=("main",))
    st.stop()

# --- 2. UNIT HISTORY VIEW ---
elif st.session_state.page == "history":
    name = st.session_state.view_target
    unit = st.session_state.network[name]
    st.title(f"📑 Tactical Audit: {name}")
    st.write(f"Asset: **{unit['label']}** | Strategy: **{unit['mode']}**")
    
    if unit['history']:
        st.dataframe(pd.DataFrame(unit['history']), use_container_width=True)
    else:
        st.info("No maneuvers recorded in logs.")
    
    st.button("Return to Terminal", on_click=go_to, args=("main",))
    st.stop()

# --- 3. MAIN TERMINAL VIEW ---
st.title("🌐 Overwatch Market Network")
st.caption(f"Network Status: Active | System Time: {datetime.now().strftime('%H:%M:%S')}")

# Global Navigation
c1, c2, _ = st.columns([1.5, 1.5, 5])
c1.button("📊 View Leaderboard", on_click=go_to, args=("leaderboard",))
if c2.button("♻️ System Refresh"): st.rerun()

st.divider()

# Deployment Grid
cols = st.columns(4)
for i, (name, unit) in enumerate(st.session_state.network.items()):
    with cols[i]:
        st.subheader(name)
        st.write(f"**Asset:** {unit['label']}")
        
        df = fetch_telemetry(unit['ticker'], unit['mode'])
        if df is not None:
            price = df['Close'].iloc[-1]
            equity = unit['balance'] + (unit['units'] * price)
            gain = ((equity - 100.0) / 100.0) * 100
            
            # Metric Container with Black Text for Price
            st.metric("Price (USD)", f"${price:,.2f}")
            st.metric("Performance", f"€{equity:.2f}", f"{gain:+.2f}%")
            
            # Logic Processing
            if unit['units'] == 0:
                unit['thought'] = "Scanning for entry point"
                if price <= df['Lower'].iloc[-1]:
                    unit['units'] = unit['balance'] / price
                    unit['balance'] = 0
                    unit['history'].append({"Time": datetime.now().strftime("%H:%M:%S"), "Type": "BUY", "Price": price})
                    unit['status'] = "HOLDING"
            else:
                unit['thought'] = "Monitoring exit parameters"
                if price >= df['Upper'].iloc[-1]:
                    unit['balance'] = unit['units'] * price
                    unit['units'] = 0
                    unit['history'].append({"Time": datetime.now().strftime("%H:%M:%S"), "Type": "SELL", "Price": price})
                    unit['status'] = "LIQUIDATED"
                elif gain <= -3.0:
                    unit['balance'] = unit['units'] * price
                    unit['units'] = 0
                    unit['history'].append({"Time": datetime.now().strftime("%H:%M:%S"), "Type": "EXIT (STOP)", "Price": price})
                    unit['status'] = "STOP LOSS"

            # Clean logic display (removed "Logic:" prefix)
            st.info(unit['thought'])
            st.button(f"Analyze Unit", key=f"btn_{name}", on_click=go_to, args=("history", name))

# Network Summary Footer
st.divider()
total_net = sum([u['balance'] + (u['units'] * yf.Ticker(u['ticker']).fast_info['last_price']) for u in st.session_state.network.values()])
st.write(f"**Combined Network Value:** €{total_net:.2f}")

time.sleep(15)
st.rerun()
