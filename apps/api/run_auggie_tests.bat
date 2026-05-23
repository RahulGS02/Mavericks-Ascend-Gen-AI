@echo off
echo ================================================================================
echo                    Auggie SDK Setup and Testing
echo ================================================================================
echo.

REM Check if we're in the correct directory
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please run this script from the apps/api directory
    pause
    exit /b 1
)

echo Step 1: Checking Python environment...
python --version
echo.

echo Step 2: Checking if auggie-sdk is installed...
python -c "import auggie_sdk; print(f'auggie-sdk version: {auggie_sdk.__version__ if hasattr(auggie_sdk, \"__version__\") else \"unknown\"}')" 2>nul

if errorlevel 1 (
    echo.
    echo WARNING: auggie-sdk is NOT installed!
    echo.
    choice /C YN /M "Do you want to install auggie-sdk now"
    if errorlevel 2 goto skip_install
    if errorlevel 1 goto install_sdk
) else (
    echo auggie-sdk is installed!
    goto run_tests
)

:install_sdk
echo.
echo Installing auggie-sdk...
pip install auggie-sdk
if errorlevel 1 (
    echo ERROR: Failed to install auggie-sdk
    pause
    exit /b 1
)
echo auggie-sdk installed successfully!
goto run_tests

:skip_install
echo.
echo Skipping auggie-sdk installation...
echo Some tests may fail without auggie-sdk installed.
echo.

:run_tests
echo.
echo ================================================================================
echo                    Running Tests
echo ================================================================================
echo.

echo Test 1: Environment Variable Loading
echo --------------------------------------------------------------------------------
python test_env_loading.py
echo.
echo.

echo Press any key to continue to Test 2...
pause > nul

echo Test 2: Auggie SDK DirectContext Test
echo --------------------------------------------------------------------------------
python test_auggie_sdk.py
echo.
echo.

echo Press any key to continue to Test 3...
pause > nul

echo Test 3: Auggie API Connection Test
echo --------------------------------------------------------------------------------
echo Installing httpx if needed...
pip install httpx >nul 2>&1
python test_auggie_connection.py
echo.
echo.

echo ================================================================================
echo                    All Tests Complete!
echo ================================================================================
echo.
echo Next Steps:
echo 1. If all tests passed, start the backend with: uvicorn app.main:app --reload
echo 2. Visit http://localhost:8000/docs to test AI endpoints
echo 3. Check AI status at: GET /api/v1/ai/status
echo.
pause
