@echo off
echo ========================================
echo FoodXchange Safety Check
echo ========================================
echo.

echo 🔍 Checking Git status...
git status

echo.
echo 🔍 Checking server status...
netstat -an | findstr :8000

echo.
echo 🔍 Checking Python environment...
python --version

echo.
echo 🔍 Checking project files...
if exist "app.py" (
    echo ✅ app.py exists
) else (
    echo ❌ app.py missing
)

if exist "database.py" (
    echo ✅ database.py exists
) else (
    echo ❌ database.py missing
)

if exist "requirements.txt" (
    echo ✅ requirements.txt exists
) else (
    echo ❌ requirements.txt missing
)

echo.
echo ========================================
echo Safety Check Complete!
echo ========================================
echo.
echo 📋 Next Steps:
echo 1. Review Git status above
echo 2. Commit changes if needed
echo 3. Start server if not running
echo 4. Test application functionality
echo.
pause 