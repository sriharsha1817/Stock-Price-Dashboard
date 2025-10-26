import gradio as gr
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

def get_stock_price(symbol):
    """Get current stock price and basic info"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period="5d")
        
        if hist.empty:
            return None
            
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'price': current_price,
            'change': change,
            'change_pct': change_pct,
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'volume': hist['Volume'].iloc[-1] if not hist.empty else 'N/A'
        }
    except Exception as e:
        return None

def get_alpha_vantage_news(symbol):
    """Get news from Alpha Vantage API"""
    if not ALPHA_VANTAGE_API_KEY:
        return []
    
    try:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        results = []
        if 'feed' in data:
            for item in data['feed'][:3]:
                title = item.get('title', '')
                url = item.get('url', '')
                if title and url:
                    results.append((title, url))
        
        return results
    except:
        return []

def get_stock_news(symbol):
    """Get news using Alpha Vantage first, fallback to yfinance"""
    # Try Alpha Vantage first
    if ALPHA_VANTAGE_API_KEY:
        alpha_news = get_alpha_vantage_news(symbol)
        if alpha_news:
            return alpha_news
    
    # Fallback to yfinance
    try:
        stock = yf.Ticker(symbol)
        news = stock.news
        
        results = []
        for item in news[:3]:
            title = item.get('title', '')
            url = item.get('link', '')
            if title and url:
                results.append((title, url))
        
        return results
    except:
        return []

def extract_stock_symbol(message):
    """Extract stock symbol from message"""
    message_lower = message.lower()
    
    # Common stock mappings
    stock_map = {
        'tesla': 'TSLA', 'tsla': 'TSLA',
        'apple': 'AAPL', 'aapl': 'AAPL', 
        'microsoft': 'MSFT', 'msft': 'MSFT',
        'google': 'GOOGL', 'googl': 'GOOGL', 'alphabet': 'GOOGL',
        'amazon': 'AMZN', 'amzn': 'AMZN',
        'meta': 'META', 'facebook': 'META',
        'nvidia': 'NVDA', 'nvda': 'NVDA',
        'netflix': 'NFLX', 'nflx': 'NFLX'
    }
    
    # Check for direct symbol matches first
    words = message_lower.split()
    for word in words:
        if word.upper() in ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 'SNAP', 'UBER', 'ZOOM']:
            return word.upper()
    
    # Check for company name matches
    for name, symbol in stock_map.items():
        if name in message_lower:
            return symbol
    
    return None

def get_technical_analysis(symbol, period="1mo"):
    """Get technical analysis for a stock"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return None
            
        # Calculate simple moving averages
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        
        # Calculate RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['SMA_20'].iloc[-1]
        sma_50 = hist['SMA_50'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        return {
            'current_price': current_price,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': current_rsi,
            'trend': 'Bullish' if current_price > sma_20 > sma_50 else 'Bearish' if current_price < sma_20 < sma_50 else 'Neutral'
        }
    except Exception as e:
        return None

def process_query(message):
    """Process user query and provide accurate responses"""
    message_lower = message.lower()
    
    # Handle comparison queries FIRST
    if any(word in message_lower for word in ['vs', 'versus', 'compare', 'comparison', ' and ']):
        # Extract symbols for comparison
        symbols = []
        words = message_lower.replace('vs', ' ').replace('versus', ' ').replace('compare', ' ').replace('with', ' ').replace('and', ' ').split()
        
        # Check for direct symbols
        for word in words:
            if word.upper() in ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX']:
                symbols.append(word.upper())
        
        # Check for company names
        stock_map = {'apple': 'AAPL', 'tesla': 'TSLA', 'microsoft': 'MSFT', 'google': 'GOOGL', 'amazon': 'AMZN', 'meta': 'META', 'nvidia': 'NVDA', 'netflix': 'NFLX'}
        for name, symbol in stock_map.items():
            if name in message_lower and symbol not in symbols:
                symbols.append(symbol)
        
        if len(symbols) >= 2:
            comparison_data = []
            for symbol in symbols[:3]:
                data = get_stock_price(symbol)
                if data:
                    comparison_data.append(data)
            
            if comparison_data:
                response = "**Stock Comparison:**\n\n"
                for data in comparison_data:
                    response += f"**{data['symbol']}:** ${data['price']:.2f} ({'+' if data['change'] >= 0 else ''}{data['change']:.2f}, {data['change_pct']:.2f}%)\n"
                
                best = max(comparison_data, key=lambda x: x['change_pct'])
                worst = min(comparison_data, key=lambda x: x['change_pct'])
                
                response += f"\n🏆 **Best Today:** {best['symbol']} ({best['change_pct']:.2f}%)\n"
                response += f"📉 **Worst Today:** {worst['symbol']} ({worst['change_pct']:.2f}%)\n"
                
                return response
        
        return "Please specify stocks to compare. Example: 'compare AAPL vs TSLA' or 'MSFT and GOOGL'"
    
    # Check for stock price queries
    elif any(word in message_lower for word in ['price', 'stock price', 'current price', 'trading at']):
        symbol = extract_stock_symbol(message)
        
        if symbol:
            data = get_stock_price(symbol)
            if data:
                response = f"**{data['name']} ({data['symbol']})**\n\n"
                response += f"💰 **Current Price:** ${data['price']:.2f}\n"
                response += f"📈 **Change:** ${data['change']:.2f} ({data['change_pct']:.2f}%)\n"
                if data['market_cap'] != 'N/A':
                    response += f"🏢 **Market Cap:** ${data['market_cap']:,}\n"
                if data['pe_ratio'] != 'N/A':
                    response += f"📊 **P/E Ratio:** {data['pe_ratio']:.2f}\n"
                response += f"📊 **Volume:** {data['volume']:,}\n"
                
                # Add technical analysis
                tech = get_technical_analysis(symbol)
                if tech:
                    response += f"\n**Technical Analysis:**\n"
                    response += f"📈 **Trend:** {tech['trend']}\n"
                    response += f"📊 **RSI:** {tech['rsi']:.2f}\n"
                    response += f"📉 **20-day SMA:** ${tech['sma_20']:.2f}\n"
                    response += f"📉 **50-day SMA:** ${tech['sma_50']:.2f}\n"
                
                return response
            else:
                return f"Sorry, couldn't fetch current price data for {symbol}. Please verify the ticker symbol."
    
    # Check for news queries
    elif any(word in message_lower for word in ['news', 'latest', 'headlines', 'updates']):
        symbol = extract_stock_symbol(message)
        
        if symbol:
            news_results = get_stock_news(symbol)
            
            if news_results:
                response = f"**Latest News about {symbol}:**\n\n"
                for i, (title, url) in enumerate(news_results, 1):
                    response += f"{i}. **{title}**\n   🔗 [Read more]({url})\n\n"
                response += "\n*Source: Yahoo Finance*"
                return response
            else:
                return f"**No recent news found for {symbol}.**\n\nTry visiting [Yahoo Finance](https://finance.yahoo.com/quote/{symbol}/news) or [MarketWatch](https://www.marketwatch.com/) for the latest updates."
        else:
            return "**Please specify a stock symbol or company name for news.**\n\nExample: 'news about AAPL' or 'Tesla latest news'"
    
    # Technical indicator explanations
    elif 'macd' in message_lower:
        return """**MACD (Moving Average Convergence Divergence)**

MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security's price.

**Components:**
• **MACD Line:** 12-day EMA - 26-day EMA
• **Signal Line:** 9-day EMA of MACD line
• **Histogram:** MACD line - Signal line

**Interpretation:**
📈 **Bullish Signal:** MACD crosses above signal line
📉 **Bearish Signal:** MACD crosses below signal line
🎯 **Divergence:** Price and MACD move in opposite directions

**Usage:** Best used in trending markets to identify momentum changes."""
    
    elif 'rsi' in message_lower:
        return """**RSI (Relative Strength Index)**

RSI is a momentum oscillator that measures the speed and change of price movements, ranging from 0 to 100.

**Calculation:** RSI = 100 - (100 / (1 + RS))
Where RS = Average Gain / Average Loss over 14 periods

**Interpretation:**
🔴 **Overbought:** RSI > 70 (potential sell signal)
🟢 **Oversold:** RSI < 30 (potential buy signal)
🟡 **Neutral:** RSI between 30-70

**Usage:** Helps identify potential reversal points and momentum shifts."""
    
    elif any(word in message_lower for word in ['nifty', 'sensex', 'index']):
        if 'nifty' in message_lower:
            return """**Nifty 50 Index**

The Nifty 50 is India's benchmark stock market index representing the weighted average of 50 of the largest Indian companies listed on the National Stock Exchange (NSE).

**Key Features:**
• **Base Year:** 1995 (Base value: 1000)
• **Market Cap:** Represents ~65% of total market cap
• **Sectors:** IT, Banking, FMCG, Auto, Pharma, etc.
• **Rebalancing:** Semi-annual review

**Top Holdings:** Reliance, TCS, HDFC Bank, Infosys, ICICI Bank

**Usage:** Benchmark for Indian equity market performance and basis for index funds/ETFs."""
        
        elif 'sensex' in message_lower:
            return """**BSE Sensex**

The Sensex is India's oldest stock market index comprising 30 well-established and financially sound companies listed on the Bombay Stock Exchange (BSE).

**Key Features:**
• **Base Year:** 1978-79 (Base value: 100)
• **Market Cap:** Free-float market capitalization weighted
• **Companies:** 30 largest and most actively traded stocks
• **Rebalancing:** Periodic review by index committee

**Top Holdings:** Reliance, TCS, HDFC Bank, Infosys, Hindustan Unilever

**Usage:** Barometer of Indian stock market performance and economic health."""
    
    # Handle any other query as a general stock inquiry
    else:
        symbol = extract_stock_symbol(message)
        
        if symbol:
            # Provide comprehensive stock info
            data = get_stock_price(symbol)
            if data:
                response = f"**{data['name']} ({data['symbol']}) Overview:**\n\n"
                response += f"💰 **Price:** ${data['price']:.2f} "
                response += f"({'+' if data['change'] >= 0 else ''}{data['change']:.2f}, {data['change_pct']:.2f}%)\n\n"
                
                if data['market_cap'] != 'N/A':
                    response += f"🏢 **Market Cap:** ${data['market_cap']:,}\n"
                if data['pe_ratio'] != 'N/A':
                    response += f"📊 **P/E Ratio:** {data['pe_ratio']:.2f}\n"
                
                # Add technical analysis
                tech = get_technical_analysis(symbol)
                if tech:
                    response += f"\n**Technical Analysis:**\n"
                    response += f"📈 **Trend:** {tech['trend']}\n"
                    response += f"📊 **RSI:** {tech['rsi']:.2f}\n"
                
                response += f"\n💡 **Try:**\n"
                response += f"• 'news about {symbol}'\n"
                response += f"• 'compare {symbol} vs [other stock]'"
                
                return response
            else:
                return f"**Could not fetch data for {symbol}.**\n\nPlease verify the ticker symbol or try:\n• Stock prices: 'AAPL price'\n• News: 'news about Tesla'\n• Analysis: 'What is MACD?'"
        
        # Handle predictions and forecasts with analysis
        if any(word in message_lower for word in ['predict', 'forecast', 'future', 'next week', 'top stock', 'best stock', 'expected', 'trend']):
            # Provide current top performers with technical analysis
            top_stocks = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL']
            performance_data = []
            
            for symbol in top_stocks:
                data = get_stock_price(symbol)
                if data:
                    tech = get_technical_analysis(symbol)
                    data['tech'] = tech
                    performance_data.append(data)
            
            if performance_data:
                # Sort by performance
                performance_data.sort(key=lambda x: x['change_pct'], reverse=True)
                
                response = f"**Current Market Analysis (Based on Recent Performance):**\n\n"
                response += "⚠️ *Disclaimer: This is not financial advice. Past performance doesn't guarantee future results.*\n\n"
                
                for i, data in enumerate(performance_data[:3], 1):
                    response += f"{i}. **{data['symbol']}:** ${data['price']:.2f} ({data['change_pct']:.2f}%)\n"
                    if data['tech']:
                        response += f"   Trend: {data['tech']['trend']}, RSI: {data['tech']['rsi']:.1f}\n"
                    response += "\n"
                
                response += "**For better analysis, ask:**\n"
                response += "• 'NVDA technical analysis' for detailed indicators\n"
                response += "• 'compare AAPL vs TSLA' for direct comparison\n"
                response += "• 'news about [stock]' for market sentiment"
                
                return response
        
        # Handle any other question intelligently
        return f"**Your question: \"{message}\"**\n\n**I can provide:**\n📊 Real-time stock prices & analysis\n📰 Latest news for any company\n📈 Technical indicators (MACD, RSI)\n🔍 Stock comparisons\n💡 Market insights\n\n**Examples:**\n• \"AAPL price\" \n• \"news about TSLA\"\n• \"compare MSFT vs GOOGL\"\n• \"What is RSI?\""

def chat_function(message, history):
    """Main chat function with enhanced responses"""
    if not message.strip():
        return "Please enter a question about stocks, prices, or financial terms."
    
    try:
        response = process_query(message)
        return response
    except Exception as e:
        return f"Sorry, I encountered an error processing your request: {str(e)}. Please try again."

# Create enhanced Gradio interface
with gr.Blocks(title="Enhanced Stock RAG Chatbot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📈 Enhanced Stock RAG Chatbot")
    gr.Markdown("""
    **Get real-time stock data, news, and financial insights!**
    
    ✅ **Real-time stock prices** with technical analysis  
    ✅ **Stock comparisons** and performance metrics  
    ✅ **Latest news** from Yahoo Finance  
    ✅ **Technical indicators** explanations (MACD, RSI)  
    ✅ **Market indices** information (Nifty 50, Sensex)
    """)
    
    chatbot = gr.Chatbot(
        height=600, 
        type="messages",
        placeholder="Ask me about stock prices, news, or financial terms!"
    )
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="e.g., 'AAPL price', 'news about TSLA', 'What is MACD?'",
            label="Your Question",
            scale=4
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)
    
    clear = gr.Button("Clear Chat", variant="secondary")
    
    # Enhanced examples
    gr.Markdown("### 💡 Try these examples:")
    with gr.Row():
        gr.Button("AAPL price", size="sm").click(lambda: "AAPL stock price", None, msg)
        gr.Button("news about TSLA", size="sm").click(lambda: "news about TSLA", None, msg)
        gr.Button("compare AAPL vs TSLA", size="sm").click(lambda: "compare AAPL and TSLA", None, msg)
        gr.Button("What is RSI?", size="sm").click(lambda: "What is RSI indicator?", None, msg)
    
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history
            
        bot_message = chat_function(message, chat_history)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return "", chat_history
    
    # Event handlers
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    send_btn.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)

if __name__ == "__main__":
    print("[INFO] Starting Enhanced Stock RAG Chatbot...")
    print("[INFO] Features: Real-time prices + News + Technical analysis")
    print("[INFO] Powered by yfinance and web scraping")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7865,
        share=True,
        show_error=True
    )