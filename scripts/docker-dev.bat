@echo off
:: FoodXchange Docker Development Script for Windows
:: This provides an interactive menu for Docker development

setlocal enabledelayedexpansion

:: Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

:menu
cls
echo ===================================
echo   FoodXchange Docker Development
echo ===================================
echo.
echo 1. Start Development Environment
echo 2. Stop Development Environment
echo 3. View Container Status
echo 4. View Logs
echo 5. Run Azure Health Check
echo 6. Open Web Shell
echo 7. Open Database Console
echo 8. Restart Services
echo 9. Rebuild Containers
echo 10. Run Tests
echo 0. Exit
echo.
set /p choice=Select option: 

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto status
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto health
if "%choice%"=="6" goto shell
if "%choice%"=="7" goto database
if "%choice%"=="8" goto restart
if "%choice%"=="9" goto rebuild
if "%choice%"=="10" goto tests
if "%choice%"=="0" exit /b

echo Invalid option. Please try again.
pause
goto menu

:start
echo Starting FoodXchange development environment...
docker-compose up -d
echo.
echo Services started! Access at:
echo - Application: http://localhost:8003
echo - Database Admin: http://localhost:8080
echo - Mail UI: http://localhost:8025
echo - Redis Commander: http://localhost:8081
pause
goto menu

:stop
echo Stopping all services...
docker-compose down
echo Services stopped.
pause
goto menu

:status
docker-compose ps
pause
goto menu

:logs
echo Select service:
echo 1. Web Application
echo 2. All Services
set /p log_choice=Select: 
if "%log_choice%"=="1" (
    docker-compose logs -f web
) else (
    docker-compose logs -f
)
goto menu

:health
echo Running Azure health check...
docker-compose exec web python quick_health_check.py
pause
goto menu

:shell
docker-compose exec web bash
goto menu

:database
docker-compose exec postgres psql -U postgres -d foodxchange
goto menu

:restart
docker-compose restart
echo Services restarted.
pause
goto menu

:rebuild
echo Rebuilding containers...
docker-compose build --no-cache
echo Rebuild complete.
pause
goto menu

:tests
echo Running tests...
docker-compose exec web python -m pytest
pause
goto menu