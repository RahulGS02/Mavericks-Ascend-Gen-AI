@echo off
echo ================================================================================
echo        MAVERICK ASCEND - COMPLETE DATABASE SETUP
echo ================================================================================
echo.

cd /d %~dp0

echo Step 1: Activating virtual environment...
call venv\Scripts\activate

echo.
echo Step 2: Running database migrations...
echo ================================================================================
alembic upgrade head

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Migration failed!
    echo    Make sure PostgreSQL is running
    pause
    exit /b 1
)

echo.
echo ✅ Migrations completed!
echo.
echo Step 3: Seeding dashboard data...
echo ================================================================================
python scripts\seed_dashboard_data.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Seeding failed!
    pause
    exit /b 1
)

echo.
echo.
echo ================================================================================
echo              ✅ SETUP COMPLETE!
echo ================================================================================
echo.
echo Database is ready with all data!
echo.
echo Next steps:
echo   1. Start backend:  uvicorn app.main:app --reload
echo   2. Start frontend: cd ..\web && npm run dev  
echo   3. Login at http://localhost:3000
echo      Email: hr@maverick.com
echo      Password: hr123
echo.
echo ================================================================================
pause
