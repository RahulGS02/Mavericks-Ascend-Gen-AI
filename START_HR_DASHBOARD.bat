@echo off
echo ================================================================================
echo        MAVERICK ASCEND - HR DASHBOARD STARTUP
echo ================================================================================
echo.

REM Step 1: Seed Dashboard Data
echo [1/3] Seeding HR Dashboard Data...
echo ================================================================================
cd apps\api
call venv\Scripts\activate
python scripts\seed_dashboard_data.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to seed data!
    echo Make sure PostgreSQL is running and database exists.
    pause
    exit /b 1
)

echo.
echo.
echo [2/3] Starting Backend Server...
echo ================================================================================
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.

start "Maverick Ascend API" cmd /k "cd /d %CD% && venv\Scripts\activate && uvicorn app.main:app --reload"

timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting Frontend...
echo ================================================================================
cd ..\web

start "Maverick Ascend Web" cmd /k "npm run dev"

echo.
echo ================================================================================
echo              ALL SERVICES STARTED!
echo ================================================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Login Credentials:
echo   HR:       hr@maverick.com / hr123
echo   Admin:    admin@maverick.com / admin123
echo   Trainer:  trainer@maverick.com / trainer123
echo.
echo ================================================================================
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping services...
taskkill /FI "WindowTitle eq Maverick Ascend API*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Maverick Ascend Web*" /T /F >nul 2>&1

echo Done!
