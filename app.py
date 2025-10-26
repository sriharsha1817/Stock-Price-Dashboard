import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from datetime import date
from prophet import Prophet
from prophet.plot import plot_plotly
import pandas as pd
import ta
from io import BytesIO
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# ---------------- CONFIG ----------------
st.set_page_config(page_title="📈 Stock Price Dashboard", layout="wide")
st.title("📈 Global Stock Price Dashboard")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Select Stock & Period")

# COMPREHENSIVE STOCK OPTIONS
ticker_options = {
    "--- Popular US Tech Stocks ---": None,
    "Apple (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", "Alphabet/Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN", "Tesla (TSLA)": "TSLA", "Meta Platforms (META)": "META",
    "NVIDIA (NVDA)": "NVDA", "Netflix (NFLX)": "NFLX", "Adobe (ADBE)": "ADBE",
    "Salesforce (CRM)": "CRM", "Oracle (ORCL)": "ORCL", "Intel (INTC)": "INTC",
    "AMD (AMD)": "AMD", "Cisco (CSCO)": "CSCO", "IBM (IBM)": "IBM",
    
    "--- US Financial & Healthcare ---": None,
    "Berkshire Hathaway (BRK-B)": "BRK-B", "J.P. Morgan Chase (JPM)": "JPM", "Visa (V)": "V",
    "Mastercard (MA)": "MA", "Bank of America (BAC)": "BAC", "Wells Fargo (WFC)": "WFC",
    "Johnson & Johnson (JNJ)": "JNJ", "Pfizer (PFE)": "PFE", "UnitedHealth (UNH)": "UNH",
    "Moderna (MRNA)": "MRNA", "AbbVie (ABBV)": "ABBV", "Merck (MRK)": "MRK",
    
    "--- US Consumer & Industrial ---": None,
    "Walmart (WMT)": "WMT", "Procter & Gamble (PG)": "PG", "Coca-Cola (KO)": "KO",
    "PepsiCo (PEP)": "PEP", "McDonald's (MCD)": "MCD", "Nike (NKE)": "NKE",
    "Home Depot (HD)": "HD", "Disney (DIS)": "DIS", "Starbucks (SBUX)": "SBUX",
    "Boeing (BA)": "BA", "Caterpillar (CAT)": "CAT", "3M (MMM)": "MMM",
    
    "--- US Energy & Utilities ---": None,
    "Exxon Mobil (XOM)": "XOM", "Chevron (CVX)": "CVX", "ConocoPhillips (COP)": "COP",
    "NextEra Energy (NEE)": "NEE", "Dominion Energy (D)": "D", "Duke Energy (DUK)": "DUK",
    
    "--- Indian Stocks (NSE) ---": None,
    "Reliance Industries (RELIANCE.NS)": "RELIANCE.NS", "Tata Consultancy (TCS.NS)": "TCS.NS",
    "HDFC Bank (HDFCBANK.NS)": "HDFCBANK.NS", "Infosys (INFY.NS)": "INFY.NS",
    "ICICI Bank (ICICIBANK.NS)": "ICICIBANK.NS", "State Bank of India (SBIN.NS)": "SBIN.NS",
    "Hindustan Unilever (HINDUNILVR.NS)": "HINDUNILVR.NS", "ITC (ITC.NS)": "ITC.NS",
    "Bharti Airtel (BHARTIARTL.NS)": "BHARTIARTL.NS", "Kotak Mahindra Bank (KOTAKBANK.NS)": "KOTAKBANK.NS",
    "Larsen & Toubro (LT.NS)": "LT.NS", "Asian Paints (ASIANPAINT.NS)": "ASIANPAINT.NS",
    "Maruti Suzuki (MARUTI.NS)": "MARUTI.NS", "Wipro (WIPRO.NS)": "WIPRO.NS",
    "HCL Technologies (HCLTECH.NS)": "HCLTECH.NS", "Tech Mahindra (TECHM.NS)": "TECHM.NS",
    
    "--- Chinese & Asian Stocks ---": None,
    "Alibaba (BABA)": "BABA", "Tencent (TCEHY)": "TCEHY", "JD.com (JD)": "JD",
    "Baidu (BIDU)": "BIDU", "NIO (NIO)": "NIO", "Pinduoduo (PDD)": "PDD",
    "Toyota Motor (TM)": "TM", "Sony (SONY)": "SONY", "SoftBank (SFTBY)": "SFTBY",
    "Samsung (005930.KS)": "005930.KS", "Taiwan Semiconductor (TSM)": "TSM",
    
    "--- European Stocks ---": None,
    "ASML Holding (ASML)": "ASML", "SAP (SAP)": "SAP", "Nestle (NSRGY)": "NSRGY",
    "LVMH (LVMUY)": "LVMUY", "Unilever (UL)": "UL", "Shell (SHEL)": "SHEL",
    "Novo Nordisk (NVO)": "NVO", "Roche (RHHBY)": "RHHBY", "Siemens (SIEGY)": "SIEGY",
    
    "--- Cryptocurrency Stocks ---": None,
    "Coinbase (COIN)": "COIN", "MicroStrategy (MSTR)": "MSTR", "Block (SQ)": "SQ",
    "PayPal (PYPL)": "PYPL", "Robinhood (HOOD)": "HOOD",
    
    "--- ETFs & Funds ---": None,
    "SPDR S&P 500 ETF (SPY)": "SPY", "Invesco QQQ (QQQ)": "QQQ", "Vanguard Total Stock (VTI)": "VTI",
    "iShares MSCI Emerging Markets (EEM)": "EEM", "Vanguard FTSE Developed (VEA)": "VEA",
    "ARK Innovation ETF (ARKK)": "ARKK", "Technology Select Sector (XLK)": "XLK",
    
    "--- Global Market Indices ---": None,
    "S&P 500 (^GSPC)": "^GSPC", "Dow Jones (^DJI)": "^DJI", "Nasdaq Composite (^IXIC)": "^IXIC",
    "Nasdaq 100 (^NDX)": "^NDX", "Russell 2000 (^RUT)": "^RUT",
    "Nifty 50 India (^NSEI)": "^NSEI", "Sensex India (^BSESN)": "^BSESN",
    "FTSE 100 UK (^FTSE)": "^FTSE", "DAX Germany (^GDAXI)": "^GDAXI",
    "CAC 40 France (^FCHI)": "^FCHI", "Nikkei 225 Japan (^N225)": "^N225",
    "Hang Seng Hong Kong (^HSI)": "^HSI", "Shanghai Composite (000001.SS)": "000001.SS"
}

# Clean the options to remove separators (None values) before passing to selectbox
display_options = {k: v for k, v in ticker_options.items() if v is not None}

selected_company = st.sidebar.selectbox("Choose Stock or Index", list(display_options.keys()))
ticker = display_options.get(selected_company)

custom_ticker = st.sidebar.text_input("Or enter a custom ticker (Access ALL stocks)", "")
if custom_ticker:
    ticker = custom_ticker.upper()

start_date = st.sidebar.date_input("Start Date", date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())

# Toggles
show_forecast = st.sidebar.checkbox("Show 30-Day Forecast (Prophet)")
show_rsi = st.sidebar.checkbox("Show RSI")
show_macd = st.sidebar.checkbox("Show MACD")

# ---------------- MAIN SECTION ----------------
if ticker:
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)

        if data.empty:
            st.error(f"⚠️ No data found for ticker '{ticker}' and date range. Please verify the ticker symbol.")
        else:
            st.subheader(f"📈 Closing Price: {ticker}")
            st.line_chart(data['Close'])

            st.subheader("🔍 Candlestick Chart")
            fig = go.Figure(data=[go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close']
            )])
            fig.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # Download buttons
            csv = data.to_csv().encode()
            st.download_button("📅 Download Data (CSV)", csv, f"{ticker}_data.csv", "text/csv")

            buf = BytesIO()
            fig.write_image(buf, format="png")
            st.download_button("📷 Download Chart (PNG)", buf.getvalue(), f"{ticker}_chart.png", "image/png")

            # RSI
            if show_rsi:
                st.subheader("📊 RSI - Relative Strength Index")
                rsi = ta.momentum.RSIIndicator(close=data['Close']).rsi()
                st.line_chart(rsi)

            # MACD
            if show_macd:
                st.subheader("📊 MACD - Moving Average Convergence Divergence")
                macd = ta.trend.MACD(data['Close'])
                macd_df = pd.DataFrame({
                    "MACD": macd.macd(),
                    "Signal": macd.macd_signal()
                })
                st.line_chart(macd_df)

            # Forecast
            if show_forecast:
                st.subheader("🔮 Forecast using Prophet (30 Days)")
                df = data.reset_index()[['Date', 'Close']]
                df['Date'] = df['Date'].dt.tz_localize(None)
                df.rename(columns={"Date": "ds", "Close": "y"}, inplace=True)

                model = Prophet()
                model.fit(df)

                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)

                forecast_plot = plot_plotly(model, forecast)
                st.plotly_chart(forecast_plot, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error fetching data for {ticker}: {e}")

# ---------------- INTEGRATED RAG CHATBOT ----------------
st.markdown("---")
st.header("💬 AI Stock Assistant")

# Chatbot functions integrated
def get_stock_news_simple(symbol):
    try:
        stock = yf.Ticker(symbol)
        news = stock.news[:3]
        return [(item.get('title', ''), item.get('link', '')) for item in news if item.get('title')]
    except:
        return []

def simple_chat_function(message):
    message_lower = message.lower()
    
    # Stock price queries
    if any(word in message_lower for word in ['price', 'stock']):
        symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NVDA']
        for symbol in symbols:
            if symbol.lower() in message_lower or symbol in message_lower:
                try:
                    stock = yf.Ticker(symbol)
                    data = stock.history(period='1d')
                    if not data.empty:
                        price = data['Close'].iloc[-1]
                        return f"**{symbol} Current Price:** ${price:.2f}"
                except:
                    pass
        return "Please specify a valid stock symbol (e.g., AAPL, TSLA)"
    
    # News queries
    elif 'news' in message_lower:
        symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NVDA']
        for symbol in symbols:
            if symbol.lower() in message_lower:
                news = get_stock_news_simple(symbol)
                if news:
                    response = f"**Latest {symbol} News:**\n\n"
                    for i, (title, url) in enumerate(news, 1):
                        response += f"{i}. {title}\n"
                    return response
        return "Please specify a stock for news (e.g., 'news about AAPL')"
    
    # Comparison
    elif any(word in message_lower for word in ['compare', 'vs']):
        return "**Stock Comparison:**\nTry asking: 'AAPL price' then 'TSLA price' to compare"
    
    # Technical indicators
    elif 'rsi' in message_lower:
        return "**RSI (Relative Strength Index):**\nMeasures if a stock is overbought (>70) or oversold (<30). Values between 30-70 are neutral."
    
    elif 'macd' in message_lower:
        return "**MACD (Moving Average Convergence Divergence):**\nShows relationship between two moving averages. When MACD crosses above signal line, it's bullish."
    
    # Default
    else:
        return f"**Ask me about:**\n• Stock prices: 'AAPL price'\n• News: 'news about TSLA'\n• Indicators: 'What is RSI?'\n• Comparisons: 'compare AAPL vs TSLA'"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about stocks, news, or technical analysis..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        response = simple_chat_function(prompt)
        st.markdown(response)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

# Example buttons
st.markdown("**Try these examples:**")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("AAPL price"):
        st.rerun()
with col2:
    if st.button("News about TSLA"):
        st.rerun()
with col3:
    if st.button("Compare AAPL vs TSLA"):
        st.rerun()
with col4:
    if st.button("What is RSI?"):
        st.rerun()
