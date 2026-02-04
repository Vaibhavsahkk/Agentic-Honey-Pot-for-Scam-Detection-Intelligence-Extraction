@echo off
echo.
echo ================================================
echo    Agentic Honey-Pot - Starting Server
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Start the server
echo.
echo Starting FastAPI server...
echo.
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
python -m app.main

pause
