@echo off
echo ========================================
echo Maverick Insights - Database Setup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Test database connection
echo.
echo Testing database connection...
python -c "from app.database import engine; print('✅ Connected to Supabase!' if engine else '❌ Connection failed')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Database connection failed
    echo Please check your .env file
    pause
    exit /b 1
)

REM Create migration
echo.
echo Creating migration...
alembic revision --autogenerate -m "Initial schema - 12 tables"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create migration
    pause
    exit /b 1
)

REM Apply migration
echo.
echo Applying migration to database...
alembic upgrade head
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to apply migration
    pause
    exit /b 1
)

REM Seed data
echo.
echo Seeding sample data...
python scripts/seed_data.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to seed data
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ DATABASE SETUP COMPLETE!
echo ========================================
echo.
echo Your database is ready with:
echo   • 12 tables created
echo   • 4 users (admin, hr, trainer, manager)
echo   • 5 sample mavericks
echo   • 1 training pipeline
echo   • 1 active batch
echo.
echo Login credentials:
echo   Admin:   admin@maverick.com / admin123
echo   HR:      hr@maverick.com / hr123
echo   Trainer: trainer@maverick.com / trainer123
echo   Manager: manager@maverick.com / manager123
echo.
echo Next: Start the API server with 'uvicorn app.main:app --reload'
echo.
pause
