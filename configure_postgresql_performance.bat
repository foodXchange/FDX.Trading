@echo off
echo ========================================
echo PostgreSQL Performance Configuration
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "foodxchange-env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call foodxchange-env\Scripts\activate.bat
) else (
    echo Virtual environment not found, using system Python...
)

echo.
echo Running PostgreSQL performance configuration...
python configure_postgresql_performance.py

echo.
echo Configuration complete!
pause 