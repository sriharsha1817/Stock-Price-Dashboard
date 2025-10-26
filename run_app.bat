@echo off
echo Setting up Stock Price Dashboard...

REM Set the API key (replace with your actual key)
set GEMINI_API_KEY=AIzaSyB_5Gwe2Tu_V7yftt9DdZXj0UJ47KXX8cQ

echo Installing dependencies...
pip install -r requirements.txt

echo Starting Streamlit application...
streamlit run app.py

pause