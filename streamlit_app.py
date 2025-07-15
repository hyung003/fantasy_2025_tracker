import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
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
    "Jensen":  "TSM",       # TSMC on NYSE
    "Simon":   "RKLB",
    "Chris":   "BMNR",
    "Alvin":   "XRP-USD",
    "Bailey":  "DOGE-USD",
    "Talent":  "SUPRA-USD",
    "Henry":   "REPL",
}

# — On first run, fetch baseline OPEN (or fallback to close)
if "open_prices" not in st.session_state:
    opens = {}
    start_str = baseline_date.strftime("%Y-%m-%d")
    end_str   = (baseline_date + timedelta(days=1)).strftime("%Y-%m-%d")
    for name, ticker in participants.items():
        try:
            hist = yf.Ticker(ticker).history(
                start=start_str, end=end_str, interval="1d"
            )
            if not hist.empty:
                opens[ticker] = hist["Open"].iloc[0]
            else:
                # fallback to the last available close
                hist2 = yf.Ticker(ticker).history(period="2d", interval="1d")
                if len(hist2) >= 2:
                    opens[ticker] = hist2["Close"].iloc[-2]
                elif len(hist2) == 1:
                    opens[ticker] = hist2["Close"].iloc[0]
                else:
                    opens[ticker] = None
        except Exception as e:
            st.warning(f"Could not fetch baseline for {ticker}: {e}")
            opens[ticker] = None
    st.session_state.open_prices = opens

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
        "Baseline Price": f"${open_price:,.2f}",
        "Current Price":  f"${current:,.2f}",
        "% Gain":         f"{pct_gain:+.2f}%"
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
