# 📈 Stock Price Dashboard with RAG Chatbot

A comprehensive financial analysis platform combining real-time stock data visualization with an AI-powered chatbot for intelligent market insights.

## 🚀 Features

### 📊 Interactive Dashboard
- **Real-time stock prices** for 100+ global stocks and indices
- **Interactive candlestick charts** with technical indicators
- **Technical analysis** (RSI, MACD, Moving Averages)
- **30-day forecasting** using Prophet algorithm
- **Data export** (CSV, PNG)

### 🤖 AI-Powered RAG Chatbot
- **Natural language queries** - Ask anything about stocks
- **Real-time news** integration via Alpha Vantage API
- **Stock comparisons** - Compare multiple stocks instantly
- **Technical analysis** explanations and education
- **Market predictions** with trend analysis

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Frontend** | Streamlit, Gradio, Plotly |
| **Data Sources** | yfinance, Alpha Vantage API |
| **AI/ML** | Prophet (forecasting), Technical Analysis |
| **Backend** | Python, pandas, requests |
| **Deployment** | Local hosting, Virtual Environment |

## 📦 Installation

### Quick Setup (Windows)
```bash
# Clone the repository
git clone <repository-url>
cd Stock_Price_Dashboard

# Run automated setup
setup_and_run.bat
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

1. **Get Alpha Vantage API Key** (Optional - for enhanced news)
   - Visit: https://www.alphavantage.co/support/#api-key
   - Get free API key (5 calls/minute)

2. **Configure Environment**
   ```bash
   # Edit .env file
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

## 🚀 Usage

### Method 1: Batch Files (Windows)
```bash
run_dashboard.bat    # Starts Streamlit dashboard
run_chatbot.bat      # Starts RAG chatbot
```

### Method 2: Manual Commands
```bash
# Terminal 1 - Dashboard
streamlit run app.py

# Terminal 2 - Chatbot  
python enhanced_rag_app.py
```



## 💡 Usage Examples

### Dashboard Queries
- Select from 100+ pre-configured stocks
- Enter custom ticker symbols (e.g., SNAP, UBER)
- Enable technical indicators and forecasting
- Export data and charts

### Chatbot Queries
```
"AAPL stock price"                    # Get Apple's current price
"news about Tesla"                    # Latest Tesla headlines  
"compare MSFT vs GOOGL"              # Stock comparison
"What is MACD?"                      # Technical indicator explanation
"top performing stocks today"         # Market analysis
"NVDA technical analysis"            # Detailed stock analysis
```

## 📊 Supported Markets

| Region | Examples | Format |
|--------|----------|--------|
| **US Stocks** | AAPL, TSLA, MSFT, GOOGL | Standard ticker |
| **Indian Stocks** | TCS.NS, RELIANCE.NS | .NS suffix |
| **Global Indices** | ^GSPC, ^NSEI, ^FTSE | ^ prefix |
| **ETFs** | SPY, QQQ, ARKK | Standard ticker |

## 🔍 Key Components

### `app.py` - Streamlit Dashboard
- Interactive stock selection (100+ options)
- Real-time price charts and candlestick visualization
- Technical indicators (RSI, MACD)
- Prophet forecasting integration
- Data export functionality

### `enhanced_rag_app.py` - AI Chatbot
- Natural language processing for stock queries
- Multi-source news integration (Alpha Vantage + yfinance)
- Intelligent stock symbol recognition
- Technical analysis explanations
- Stock comparison engine

### `requirements.txt` - Dependencies
```
streamlit>=1.28.0
yfinance>=0.2.18
plotly>=5.15.0
prophet>=1.1.4
gradio>=4.0.0
python-dotenv>=1.0.0
```

## 🎯 Project Highlights

### ✅ Intelligent Query Processing
- Handles unlimited query types
- Context-aware responses
- Educational content integration

### ✅ Multi-Source Data Integration
- Primary: Alpha Vantage API (premium news)
- Fallback: yfinance (free Yahoo Finance data)
- Graceful error handling

### ✅ Comprehensive Technical Analysis
- Real-time RSI, MACD calculations
- Trend analysis (Bullish/Bearish/Neutral)
- Moving averages (20-day, 50-day)

### ✅ Global Market Coverage
- US, Indian, European, Asian markets
- Major indices and ETFs
- Cryptocurrency-related stocks

## 🔧 Troubleshooting

### Common Issues
1. **Port conflicts**: Change ports in code (7865 → 7866)
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **API limits**: Alpha Vantage free tier: 5 calls/minute
4. **Virtual environment**: Use provided batch files

### Error Solutions
```bash
# If streamlit not found
pip install streamlit

# If gradio not found  
pip install gradio

# If yfinance issues
pip install --upgrade yfinance
```

## 📈 Future Enhancements

- [ ] Portfolio tracking and management
- [ ] Real-time alerts and notifications
- [ ] Advanced charting with more indicators
- [ ] Social sentiment analysis
- [ ] Mobile app development
- [ ] Database integration for historical analysis

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **yfinance** - Free Yahoo Finance data
- **Alpha Vantage** - Premium financial APIs
- **Streamlit** - Rapid web app development
- **Gradio** - AI interface framework
- **Prophet** - Time series forecasting

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check troubleshooting section
- Review API documentation

---

**⭐ Star this repository if you found it helpful!**
