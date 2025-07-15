import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# — Page config
st.set_page_config(page_title="📈 $100 Contest Tracker", layout="wide")

# — Timezone
pst = pytz.timezone("America/Los_Angeles")

# — Contest baseline date (market open on July 14, 2025)
baseline_date = pst.localize(datetime(2025, 7, 14, 6, 30))
contest_end   = pst.localize(datetime(2025, 7, 25, 13, 0))

# — Header
st.title("📊 Stock & Crypto $100 Contest")
now = datetime.now(pst)
st.markdown(
    f"**Contest Baseline:** {baseline_date.strftime('%b %d %Y, %I:%M %p PST')}  \n"
    f"**Contest Ends:**   {contest_end.strftime('%b %d %Y, %I:%M %p PST')}  \n"
    f"**Current Time:**   {now.strftime('%b %d, %Y %I:%M %p PST')}"
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

# — Hardcoded baseline prices
if "open_prices" not in st.session_state:
    st.session_state.open_prices = {
        "ZS": 288.2,
        "TXT": 84.66,
        "RTX": 147.89,
        "TSM": 229.33,
        "RKLB": 39.30,
        "BMNR": 47.40,
        "XRP-USD": 2.8359,
        "DOGE-USD": 0.198595,
        "SUPRA-USD": 0.004273,
        "REPL": 10.94,
    }

# — Build leaderboard
rows = []
for name, ticker in participants.items():
    open_price = st.session_state.open_prices.get(ticker)
    if open_price is None:
        continue

    try:
        info = yf.Ticker(ticker).info
        current = info.get("regularMarketPrice") or info.get("previousClose")
    except Exception as e:
        st.warning(f"Could not fetch current price for {ticker}: {e}")
        continue

    pct_gain = (current - open_price) / open_price * 100

    rows.append({
        "Friend":         name,
        "Ticker":         ticker,
        "Baseline Price": open_price,
        "Current Price":  current,
        "% Gain":         pct_gain
    })

# — Create DataFrame and sort
if rows:
    df = (pd.DataFrame(rows)
            .sort_values("% Gain", ascending=False)
            .reset_index(drop=True).assign(Row_Number=lambda x: range(1, len(x) + 1)))
else:
    df = pd.DataFrame(columns=["Friend", "Ticker", "Baseline Price", "Current Price", "% Gain"])

# — Display
st.subheader("🏆 Live Rankings")
st.dataframe(
    df.style.format({
        "Baseline Price": "${:,.2f}",
        "Current Price":  "${:,.2f}",
        "% Gain":         "{:+.2f}%"
    }),
    height=500
)

# — Highlight leader
if not df.empty:
    top = df.iloc[0]
    st.markdown(
        f"### 🥇 Leader: **{top.Friend}** ({top.Ticker}) up **{top['% Gain']:+.2f}%**"
    )

# — Last refresh timestamp
st.caption(f"Last data refresh: {st.session_state.last_refresh.strftime('%I:%M:%S %p PST')}")