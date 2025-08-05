@echo off
echo Opening FoodXchange Dashboards...
echo.

:: Open VM Access Dashboard
start "" "C:\Users\foodz\Desktop\FoodXchange\quick_vm_access.html"

:: Wait a moment
timeout /t 1 /nobreak >nul

:: Open PostgreSQL Dashboard  
start "" "C:\Users\foodz\Desktop\FoodXchange\postgres_dashboard.html"

echo.
echo ✅ Dashboards opened successfully!
echo.
echo Available dashboards:
echo - VM Access Dashboard: Control and monitor your Azure VM
echo - PostgreSQL Dashboard: Manage your database
echo.
pause