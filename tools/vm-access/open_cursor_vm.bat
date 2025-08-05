@echo off
echo Opening Cursor IDE connected to FDX VM...
echo.

REM Try to find Cursor installation
set CURSOR_PATH=
if exist "%LOCALAPPDATA%\Programs\cursor\Cursor.exe" (
    set CURSOR_PATH=%LOCALAPPDATA%\Programs\cursor\Cursor.exe
) else if exist "C:\Program Files\Cursor\Cursor.exe" (
    set CURSOR_PATH=C:\Program Files\Cursor\Cursor.exe
) else if exist "%APPDATA%\Local\Programs\cursor\Cursor.exe" (
    set CURSOR_PATH=%APPDATA%\Local\Programs\cursor\Cursor.exe
)

if "%CURSOR_PATH%"=="" (
    echo Cursor not found in standard locations.
    echo Please open Cursor manually and connect to fdx-vm
    pause
    exit /b
)

echo Found Cursor at: %CURSOR_PATH%
echo.
echo Launching Cursor with remote SSH connection...
echo.

REM Launch Cursor with remote SSH
"%CURSOR_PATH%" --remote ssh-remote+fdx-vm /home/fdxfounder/fdx/app

echo.
echo If Cursor doesn't connect automatically:
echo 1. Press Ctrl+Shift+P
echo 2. Type: Remote-SSH: Connect to Host
echo 3. Select: fdx-vm
echo.
pause