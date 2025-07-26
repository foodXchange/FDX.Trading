@echo off
echo ========================================
echo FoodXchange pgAdmin Setup Helper
echo ========================================
echo.
echo This script will help you connect to your Azure PostgreSQL database.
echo.
echo Connection Details:
echo Host: foodxchangepgfr.postgres.database.azure.com
echo Port: 5432
echo Database: foodxchange_db
echo Username: pgadmin
echo Password: Ud30078123
echo.
echo Instructions:
echo 1. pgAdmin will open automatically
echo 2. Click "Add New Server" in the Quick Links section
echo 3. Use the connection details above
echo 4. Save the connection
echo.
pause
echo.
echo Opening pgAdmin...
start "" "C:\Program Files\pgAdmin 4\bin\pgAdmin4.exe"
echo.
echo pgAdmin should now be opening.
echo Follow the step-by-step instructions in the pgadmin_setup_guide.md file.
echo.
pause 