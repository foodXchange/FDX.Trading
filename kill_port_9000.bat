@echo off
echo Killing processes on port 9000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9000 ^| findstr LISTENING') do (
    echo Killing PID %%a
    taskkill /PID %%a /F 2>nul
)
echo Done!