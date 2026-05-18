@echo off
echo ================================================================================
echo        MAVERICK ASCEND - FIX ENUM AND COMPLETE SETUP
echo ================================================================================
echo.

cd /d %~dp0

echo Step 1: Fixing enum type in database...
echo ================================================================================
echo Running SQL fix script...
psql -U postgres -d maverick_insights -f fix_enum.sql

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: SQL fix failed!
    echo.
    echo Please run manually:
    echo   psql -U postgres -d maverick_insights
    echo   Then copy-paste from fix_enum.sql
    pause
    exit /b 1
)

echo.
echo ✅ Enum fixed!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate

echo.
echo Step 3: Running database migrations...
echo ================================================================================
alembic upgrade head

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Migration failed!
    pause
    exit /b 1
)

echo.
echo ✅ Migrations completed!
echo.

echo Step 4: Seeding dashboard data...
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
echo              ✅ COMPLETE SETUP SUCCESSFUL!
echo ================================================================================
echo.
echo Database is ready with all data!
echo.
echo Next steps:
echo   1. Start backend:  uvicorn app.main:app --reload
echo   2. Start frontend: cd ..\web ^&^& npm run dev  
echo   3. Login at http://localhost:3000
echo      Email: hr@maverick.com
echo      Password: hr123
echo.
echo ================================================================================
pause
