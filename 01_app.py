import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Global Market Cap Top 10 Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("🌍 Global Market Cap Top 10 Stock Dashboard")
st.markdown("최근 **1년간** 글로벌 시가총액 Top10 기업의 주가 변화")

# 시가총액 Top10 기업 (2025~2026 기준)
companies = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Saudi Aramco": "2222.SR",
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Berkshire Hathaway": "BRK-B"
}

selected = st.multiselect(
    "기업 선택",
    list(companies.keys()),
    default=["Apple", "Microsoft", "NVIDIA"]
)

end = datetime.today()
start = end - timedelta(days=365)

fig = go.Figure()

for company in selected:
    ticker = companies[company]

    try:
        data = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
            auto_adjust=True
        )

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Close"],
                mode="lines",
                name=company,
                hovertemplate=
                "<b>%{fullData.name}</b><br>" +
                "%{x|%Y-%m-%d}<br>" +
                "$%{y:.2f}<extra></extra>"
            )
        )

    except Exception:
        st.warning(f"{company} 데이터를 불러올 수 없습니다.")

fig.update_layout(
    template="plotly_white",
    title="Stock Price (Last 1 Year)",
    xaxis_title="Date",
    yaxis_title="Adjusted Close Price",
    hovermode="x unified",
    height=700,
    legend_title="Company"
)

st.plotly_chart(fig, use_container_width=True)
