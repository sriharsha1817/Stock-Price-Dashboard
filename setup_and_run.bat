@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete! 
echo.
echo To run the project:
echo 1. Dashboard: streamlit run app.py
echo 2. Chatbot: python enhanced_rag_app.py
echo.
pause