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
now = datetime.now(pst)
st.markdown(
    f"**Contest Period:** {contest_start.strftime('%b %d %Y, %I:%M %p PST')} → "
    f"{contest_end.strftime('%b %d %Y, %I:%M %p PST')}  \n"
    f"**Current Time:** {now.strftime('%b %d, %Y %I:%M %p PST')}"
)

# — Track last refresh
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = now
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

# — On first run, grab baseline opens (or fallback to close)
if "open_prices" not in st.session_state:
    opens = {}
    start_str = contest_start.strftime("%Y-%m-%d")
    end_str   = (contest_start + timedelta(days=1)).strftime("%Y-%m-%d")
    for name, ticker in participants.items():
        hist = yf.Ticker(ticker).history(
            start=start_str, end=end_str, interval="1d", progress=False
        )
        if not hist.empty:
            opens[ticker] = hist["Open"].iloc[0]
        else:
            # fallback to most recent close
            hist2 = yf.Ticker(ticker).history(period="1d", interval="1d", progress=False)
            opens[ticker] = hist2["Close"].iloc[0] if not hist2.empty else None
    st.session_state.open_prices = opens

# — Build leaderboard
rows = []
for name, ticker in participants.items():
    open_price = st.session_state.open_prices.get(ticker)
    if open_price is None:
        continue

    info = yf.Ticker(ticker).info
    current = info.get("regularMarketPrice") or info.get("previousClose")
    pct_gain = (current - open_price) / open_price * 100

    rows.append({
        "Friend":        name,
        "Ticker":        ticker,
        "Baseline ($100 at)": f"${open_price:,.2f}",
        "Current Price": f"${current:,.2f}",
        "% Gain":        f"{pct_gain:+.2f}%"
    })

df = pd.DataFrame(rows).sort_values("% Gain", ascending=False).reset_index(drop=True)

# — Display
st.subheader("🏆 Live Rankings")
st.table(df)

if not df.empty:
    top = df.iloc[0]
    st.markdown(
        f"### 🥇 Leader: **{top.Friend}** "
        f"({top.Ticker}) up **{top['% Gain']}**"
    )

st.caption(f"Last data refresh: {st.session_state.last_refresh.strftime('%I:%M:%S %p PST')}")
