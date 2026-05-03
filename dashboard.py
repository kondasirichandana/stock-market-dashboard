
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Stock Analysis Dashboard", page_icon="📈", layout="wide")

st.title("📈 Stock Market Analysis Dashboard")
st.markdown("**Built by Konda Siri Chandana** | Python · yfinance · Streamlit")
st.markdown("---")

st.sidebar.header("🔧 Settings")
tickers = st.sidebar.multiselect(
    "Select Stocks",
    options=["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA"],
    default=["AAPL", "MSFT", "TSLA"]
)
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date   = st.sidebar.date_input("End Date",   value=pd.to_datetime("2024-12-31"))
ma_short = st.sidebar.slider("Short Moving Average (days)", 10, 100, 50)
ma_long  = st.sidebar.slider("Long Moving Average (days)",  50, 300, 200)

@st.cache_data
def load_data(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)
    return data["Close"]

if not tickers:
    st.warning("Please select at least one stock from the sidebar.")
    st.stop()

with st.spinner("Downloading stock data..."):
    df = load_data(tickers, start_date, end_date)

if isinstance(df, pd.Series):
    df = df.to_frame()

st.subheader("📊 Key Metrics")
cols = st.columns(len(tickers))
for i, ticker in enumerate(tickers):
    if ticker in df.columns:
        start_price  = df[ticker].dropna().iloc[0]
        end_price    = df[ticker].dropna().iloc[-1]
        total_return = ((end_price - start_price) / start_price) * 100
        daily_returns = df[ticker].pct_change().dropna()
        volatility   = daily_returns.std() * 100
        cols[i].metric(label=ticker, value=f"${end_price:.2f}", delta=f"{total_return:.1f}% total return")
        cols[i].caption(f"Daily volatility: {volatility:.2f}%")

st.markdown("---")

st.subheader("💹 Stock Price Over Time")
fig1 = go.Figure()
for ticker in tickers:
    if ticker in df.columns:
        fig1.add_trace(go.Scatter(x=df.index, y=df[ticker], name=ticker, mode="lines", line=dict(width=1.5)))
fig1.update_layout(xaxis_title="Date", yaxis_title="Price (USD)", hovermode="x unified", height=400, legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig1, use_container_width=True)

st.subheader(f"📉 Moving Averages — {tickers[0]}")
ticker1 = tickers[0]
if ticker1 in df.columns:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df.index, y=df[ticker1], name="Price", line=dict(color="steelblue", width=1)))
    fig2.add_trace(go.Scatter(x=df.index, y=df[ticker1].rolling(ma_short).mean(), name=f"{ma_short}-day MA", line=dict(color="orange", width=2)))
    fig2.add_trace(go.Scatter(x=df.index, y=df[ticker1].rolling(ma_long).mean(),  name=f"{ma_long}-day MA",  line=dict(color="red",    width=2)))
    fig2.update_layout(xaxis_title="Date", yaxis_title="Price (USD)", hovermode="x unified", height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("⚖️ Normalised Performance (Start = 100)")
fig3 = go.Figure()
for ticker in tickers:
    if ticker in df.columns:
        normalised = df[ticker] / df[ticker].dropna().iloc[0] * 100
        fig3.add_trace(go.Scatter(x=df.index, y=normalised, name=ticker, mode="lines", line=dict(width=1.5)))
fig3.update_layout(xaxis_title="Date", yaxis_title="Growth from start", hovermode="x unified", height=400)
st.plotly_chart(fig3, use_container_width=True)

col1, col2 = st.columns(2)
returns = df[tickers].pct_change().dropna()

with col1:
    st.subheader("📐 Return Distribution")
    fig4 = go.Figure()
    for ticker in tickers:
        if ticker in returns.columns:
            fig4.add_trace(go.Histogram(x=returns[ticker], name=ticker, opacity=0.6, nbinsx=80))
    fig4.update_layout(barmode="overlay", height=380, xaxis_title="Daily Return", yaxis_title="Number of days")
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.subheader("🔗 Correlation Heatmap")
    corr = returns[tickers].corr()
    fig5 = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, height=380)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
with st.expander("📋 View Raw Data"):
    st.dataframe(df.tail(20).round(2), use_container_width=True)

st.caption("Data sourced from Yahoo Finance via yfinance · For educational purposes only")
