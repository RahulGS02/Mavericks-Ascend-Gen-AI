@echo off
echo ================================================================================
echo           Maverick Ascend - Dashboard Data Check
echo ================================================================================
echo.

cd /d %~dp0

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Checking database data...
echo.
python check_dashboard_data.py

echo.
echo ================================================================================
echo.
echo Starting backend server...
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

uvicorn app.main:app --reload
