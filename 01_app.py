import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Global Top10 Stocks", layout="wide")

st.title("📈 Global Market Cap Top 10")

companies = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Berkshire Hathaway": "BRK-B",
    "Saudi Aramco": "2222.SR"
}

selected = st.multiselect(
    "기업 선택",
    list(companies.keys()),
    default=["Apple", "Microsoft", "NVIDIA"]
)

start = datetime.today() - timedelta(days=365)
end = datetime.today()

fig = go.Figure()

for company in selected:

    ticker = companies[company]

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start, end=end)

        if df.empty:
            st.warning(f"{company} 데이터가 없습니다.")
            continue

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name=company
            )
        )

    except Exception as e:
        st.error(f"{company}: {e}")

fig.update_layout(
    template="plotly_white",
    hovermode="x unified",
    title="Stock Price (Last 1 Year)",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    height=700
)

st.plotly_chart(fig, use_container_width=True)
