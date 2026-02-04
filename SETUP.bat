@echo off
REM Chatbot Setup Script for Windows
REM This script sets up the entire chatbot environment

echo.
echo ================================================
echo Customer Support Chatbot - One-Click Setup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [2/4] Initializing database and configuration...
python utils.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)

echo [3/4] Running system tests...
python test_system.py
if errorlevel 1 (
    echo WARNING: Some tests failed. Please check the output above.
    echo You may still be able to run the chatbot.
)

echo [4/4] Setup complete!
echo.
echo ================================================
echo Next Steps:
echo ================================================
echo.
echo 1. Configure Email (Optional):
echo    - Edit chatbot_config.json
echo    - Add your Gmail address and app password
echo.
echo 2. Start the Chatbot:
echo    - Run: streamlit run chatbot_app.py
echo    - Open: http://localhost:8501
echo.
echo 3. Start Email Service (Optional):
echo    - Run: python email_service.py
echo.
echo For more information, see README.md
echo.
pause
