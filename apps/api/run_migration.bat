@echo off
echo ================================================================================
echo           Running Trainer Feedback Migration
echo ================================================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Running migration...
alembic upgrade head

echo.
echo ================================================================================
echo Migration Complete!
echo ================================================================================
echo.
echo The trainer_feedback table has been created.
echo.
pause
