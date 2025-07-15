import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# — Page config
st.set_page_config(page_title="📈 $100 Contest Tracker", layout="wide")

# Timezone
pst = pytz.timezone("America/Los_Angeles")

# Contest window
contest_start = pst.localize(datetime(2025, 7, 15, 6, 30))
contest_end   = pst.localize(datetime(2025, 7, 25, 13, 0))

st.title("📊 Stock & Crypto $100 Contest")
st.markdown(
    f"**Contest Period:** {contest_start.strftime('%b %d %Y, %I:%M %p PST')} → "
    f"{contest_end.strftime('%b %d %Y, %I:%M %p PST')}"
)

now = datetime.now(pst)
st.markdown(f"**Current Time:** {now.strftime('%b %d, %Y %I:%M %p PST')}")

# Manual refresh
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = now
if st.button("🔄 Refresh Data"):
    st.session_state.last_refresh = datetime.now(pst)

# If it’s not yet 6:30 AM PST on July 15, don’t fetch opens
if now < contest_start:
    st.warning("⏳ The contest hasn’t started yet!  \n"
               "Open prices will be recorded at 6:30 AM PST on July 15, 2025.")
    st.caption(f"(Last refresh: {st.session_state.last_refresh.strftime('%I:%M:%S %p PST')})")
    st.stop()

# Participants
participants = {
    "Matthew": "ZS",
    "Bryan":   "TXT",
    "Vaillen": "RTX",
    "Jensen":  "TSM",
    "Simon":   "RKLB",
    "Chris":   "BMNR",
    "Alvin":   "XRP-USD",
    "Bailey":  "DOGE-USD",
    "Talent":  "SUPRA-USD",
    "Henry":   "REPL",
}

# On first pass *after* contest_start, record the opens
if "open_prices" not in st.session_state:
    opens = {}
    # We pull the DAILY bar for the contest_start date
    start_str = contest_start.strftime("%Y-%m-%d")
    end_str   = (contest_start + timedelta(days=1)).strftime("%Y-%m-%d")
    for name, ticker in participants.items():
        hist = yf.Ticker(ticker).history(
            start=start_str, end=end_str, interval="1d", progress=False
        )
        if not hist.empty:
            opens[ticker] = hist["Open"].iloc[0]
        else:
            opens[ticker] = None
    st.session_state.open_prices = opens

# Build the leaderboard
rows = []
for name, ticker in participants.items():
    open_price = st.session_state.open_prices.get(ticker)
    if open_price is None:
        # Couldn’t get an open – skip or handle specially
        continue

    info = yf.Ticker(ticker).info
    current = info.get("regularMarketPrice") or info.get("previousClose")
    pct_gain = (current - open_price) / open_price * 100

    rows.append({
        "Friend":        name,
        "Ticker":        ticker,
        "Open Price":    open_price,
        "Current Price": current,
        "% Gain":        pct_gain,
    })

df = (pd.DataFrame(rows)
        .sort_values("% Gain", ascending=False)
        .reset_index(drop=True))

# Display
st.subheader("🏆 Live Rankings")
st.dataframe(
    df.style.format({
        "Open Price":    "${:,.2f}",
        "Current Price": "${:,.2f}",
        "% Gain":        "{:+.2f}%"
    }),
    height=500,
)

if not df.empty:
    top = df.iloc[0]
    st.markdown(
        f"### 🥇 Leader: **{top.Friend}** "
        f"({top.Ticker}) up **{top['% Gain']:.2f}%**"
    )

st.caption(f"Last data refresh: {st.session_state.last_refresh.strftime('%I:%M:%S %p PST')}")
