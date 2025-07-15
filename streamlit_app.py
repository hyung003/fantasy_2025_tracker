import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# — Page config
st.set_page_config(page_title="📈 $100 Contest Tracker", layout="wide")

# Timezone
pst = pytz.timezone("America/Los_Angeles")

# — Contest window
contest_start = datetime(2025, 7, 15, 6, 30, tzinfo=pst)
contest_end   = datetime(2025, 7, 25, 13, 0,  tzinfo=pst)

st.title("📊 Stock & Crypto $100 Contest")
st.markdown(
    f"**Contest Period:** {contest_start.strftime('%b %d %Y, %I:%M %p PST')} → "
    f"{contest_end.strftime('%b %d %Y, %I:%M %p PST')}"
)

# — Track last refresh
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now(pst)

if st.button("🔄 Refresh Data"):
    st.session_state.last_refresh = datetime.now(pst)

# — Participants & tickers
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

# — On first run, fetch and store all open prices for contest_start
if "open_prices" not in st.session_state:
    opens = {}
    # we ask yfinance for the daily bar on contest_start’s date
    start_str = contest_start.strftime("%Y-%m-%d")
    next_day  = (contest_start + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    for name, ticker in participants.items():
        hist = yf.Ticker(ticker).history(
            start=start_str, end=next_day, interval="1d"
        )
        if not hist.empty:
            opens[ticker] = hist["Open"].iloc[0]
        else:
            opens[ticker] = None
    st.session_state.open_prices = opens

# — Build leaderboard using stored opens
rows = []
for name, ticker in participants.items():
    open_price = st.session_state.open_prices.get(ticker)
    if open_price is None:
        continue

    # get live price
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

df = (
    pd.DataFrame(rows)
      .sort_values("% Gain", ascending=False)
      .reset_index(drop=True)
)

# — Display
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
