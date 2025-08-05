@echo off
title Cursor VM Control Center
color 0A

:MENU
cls
echo ============================================================
echo              CURSOR VM CONTROL CENTER
echo ============================================================
echo.
echo   VM: fdxfounder@4.206.1.15
echo   Apps: FoodXchange (Port 80) + FDX Crawler (Port 8003)
echo.
echo ============================================================
echo.
echo   [1] Open FoodXchange in Cursor (Main App - Port 80)
echo   [2] Open FDX Crawler in Cursor (23,206 Suppliers - Port 8003)
echo   [3] Open VM Root in Cursor (Full Access)
echo.
echo   [4] Start SSH Tunnel (Access blocked services locally)
echo   [5] Test SSH Connection
echo   [6] Install Cursor Remote-SSH Extension
echo.
echo   [7] View SSH Config
echo   [8] Open Command Palette Guide
echo.
echo   [0] Exit
echo.
echo ============================================================
set /p choice="Select an option (0-8): "

if "%choice%"=="1" goto FOODXCHANGE
if "%choice%"=="2" goto CRAWLER
if "%choice%"=="3" goto VMROOT
if "%choice%"=="4" goto TUNNEL
if "%choice%"=="5" goto TESTCONN
if "%choice%"=="6" goto INSTALL_EXT
if "%choice%"=="7" goto VIEWCONFIG
if "%choice%"=="8" goto PALETTE_GUIDE
if "%choice%"=="0" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MENU

:FOODXCHANGE
echo.
echo Opening FoodXchange in Cursor...
cursor --folder-uri "vscode-remote://ssh-remote+fdx-foodxchange/home/fdxfounder/fdx/app"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:CRAWLER
echo.
echo Opening FDX Crawler in Cursor...
cursor --folder-uri "vscode-remote://ssh-remote+fdx-crawler/home/fdxfounder/fdx/crawler"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:VMROOT
echo.
echo Opening VM root directory in Cursor...
cursor --folder-uri "vscode-remote://ssh-remote+fdx-vm/home/fdxfounder"
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:TUNNEL
echo.
echo Starting SSH tunnel for local access to blocked services...
echo.
echo This will forward:
echo - http://localhost:8000 -> VM Port 80 (FoodXchange)
echo - http://localhost:8003 -> VM Port 8003 (FDX Crawler)
echo - http://localhost:3000 -> VM Port 3000 (Grafana)
echo - http://localhost:19999 -> VM Port 19999 (Netdata)
echo.
echo Press Ctrl+C to stop the tunnel
echo.
ssh -i %USERPROFILE%\.ssh\fdx_founders_key fdx-dev-tunnel
pause
goto MENU

:TESTCONN
echo.
echo Testing SSH connection to VM...
echo.
ssh -o ConnectTimeout=5 fdx-vm "echo 'Connection successful!' && uname -a && echo && df -h / && echo && free -h"
echo.
pause
goto MENU

:INSTALL_EXT
echo.
echo Installing Cursor Remote-SSH extension...
cursor --install-extension ms-vscode-remote.remote-ssh --force
echo.
echo Extension installed. Restart Cursor if needed.
pause
goto MENU

:VIEWCONFIG
echo.
echo Current SSH Configuration:
echo ============================================================
type %USERPROFILE%\.ssh\config
echo ============================================================
echo.
pause
goto MENU

:PALETTE_GUIDE
cls
echo ============================================================
echo           CURSOR COMMAND PALETTE GUIDE
echo ============================================================
echo.
echo To show Command Palette: Ctrl+Shift+P
echo.
echo Useful Commands:
echo - "Remote-SSH: Connect to Host" - Connect to a configured host
echo - "Remote-SSH: Open SSH Configuration File" - Edit SSH config
echo - "Remote-SSH: Kill VS Code Server on Host" - Fix connection issues
echo - "Remote: Close Remote Connection" - Disconnect from VM
echo.
echo Quick Tips:
echo 1. After pressing Ctrl+Shift+P, start typing to filter commands
echo 2. Use arrow keys to navigate, Enter to select
echo 3. Press Escape to close the palette
echo.
echo To make Command Palette more visible:
echo 1. Go to File -> Preferences -> Settings
echo 2. Search for "command palette"
echo 3. Enable "Workbench > Command Palette: Preserve Input"
echo.
pause
goto MENU

:EXIT
echo.
echo Thank you for using Cursor VM Control Center!
timeout /t 2 >nul
exit