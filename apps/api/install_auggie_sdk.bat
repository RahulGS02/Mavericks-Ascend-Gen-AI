@echo off
echo ================================================================================
echo                    Install Auggie SDK
echo ================================================================================
echo.

echo This script will install the Auggie SDK package for AI integration.
echo.

REM Check Python
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

REM Install auggie-sdk
echo Installing auggie-sdk...
echo.
pip install auggie-sdk

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ERROR: Failed to install auggie-sdk
    echo ================================================================================
    echo.
    echo Troubleshooting:
    echo 1. Make sure you're in the virtual environment: venv\Scripts\activate
    echo 2. Try: pip install --upgrade pip
    echo 3. Try: pip install auggie-sdk --no-cache-dir
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SUCCESS! auggie-sdk installed successfully
echo ================================================================================
echo.

REM Verify installation
echo Verifying installation...
python -c "import auggie_sdk; print(f'✅ auggie-sdk version: {auggie_sdk.__version__ if hasattr(auggie_sdk, \"__version__\") else \"installed\"}')"

if errorlevel 1 (
    echo ⚠️  Warning: auggie-sdk installed but cannot be imported
) else (
    echo ✅ Installation verified!
)

echo.
echo ================================================================================
echo Next Steps:
echo ================================================================================
echo.
echo 1. Run tests: python run_auggie_tests.bat
echo 2. Or test individually: python test_auggie_sdk.py
echo 3. Start backend: uvicorn app.main:app --reload
echo 4. Visit: http://localhost:8000/docs
echo.
pause
