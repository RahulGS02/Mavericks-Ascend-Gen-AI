@echo off
REM Run Skill Similarity Engine Unit Tests

echo ================================================
echo Running Skill Similarity Engine Unit Tests
echo ================================================
echo.

cd %~dp0

REM Set test environment variables
set TESTING=true
set DATABASE_URL=postgresql://test:test@localhost:5432/test_db
set SUPABASE_URL=http://localhost:54321
set SUPABASE_SERVICE_KEY=test_key_for_testing
set JWT_SECRET=test_secret_key_for_testing_only
set ENVIRONMENT=test

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo Environment: TEST MODE
echo Running tests...
echo.

python -m pytest tests/test_skill_similarity_engine.py -v --tb=short

echo.
echo ================================================
echo Test execution complete!
echo ================================================
echo.

pause
