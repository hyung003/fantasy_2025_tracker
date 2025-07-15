import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz


# — Page config
st.set_page_config(
    page_title="📈 $100 Contest Tracker",
    layout="wide",
)

# Timezone
pst = pytz.timezone("America/Los_Angeles")

# — Header
st.title("📊 Stock & Crypto $100 Contest")

# Show current wall-clock time
now = datetime.now(pst)
st.markdown(
    f"**Contest Period:** July 15 2025, 6:30 AM PST → July 25 2025, 1:00 PM PST  \n"
    f"**Current Time:** {now.strftime('%b %d, %Y %I:%M %p PST')}"
)

# — Initialize last-refresh in session state
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = now

# — Manual refresh button
if st.button("🔄 Refresh Data"):
    st.session_state.last_refresh = datetime.now(pst)

# — Participants & tickers
participants = {
    "Matthew": "ZS",
    "Bryan":    "TXT",
    "Vaillen":  "RTX",
    "Jensen":   "TSM",
    "Simon":    "RKLB",
    "Chris":    "BMNR",
    "Alvin":    "XRP-USD",
    "Bailey":   "DOGE-USD",
    "Talent":   "SUPRA-USD",
    "Henry":    "REPL",
}

# — Fetch & compute gains
rows = []
for name, ticker in participants.items():
    t = yf.Ticker(ticker)
    hist = t.history(period="1d", interval="1d")
    if hist.empty:
        continue
    open_price    = hist["Open"].iloc[0]
    current_price = t.info.get("regularMarketPrice", hist["Close"].iloc[-1])
    pct_gain      = (current_price - open_price) / open_price * 100

    rows.append({
        "Friend":        name,
        "Ticker":        ticker,
        "Open Price":    open_price,
        "Current Price": current_price,
        "% Gain":        pct_gain,
    })

df = pd.DataFrame(rows).sort_values("% Gain", ascending=False).reset_index(drop=True)

# — Display leaderboard
st.subheader("🏆 Live Rankings")
st.dataframe(
    df.style.format({
        "Open Price":    "${:,.2f}",
        "Current Price": "${:,.2f}",
        "% Gain":        "{:+.2f}%"
    }),
    height=500,
)

# — Highlight leader
if not df.empty:
    leader = df.iloc[0]
    st.markdown(
        f"### 🥇 Leader: **{leader.Friend}** "
        f"({leader.Ticker}) up **{leader['% Gain']:.2f}%**"
    )


# — Show last refresh timestamp
st.caption(f"Last data refresh: {st.session_state.last_refresh.strftime('%I:%M:%S %p PST')}")