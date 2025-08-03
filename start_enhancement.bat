@echo off
echo Starting continuous supplier enhancement...
echo Press Ctrl+C to stop at any time

:loop
echo.
echo Running enhancement batch...
C:\Users\foodz\AppData\Local\Programs\Python\Python312\python.exe enhance_batch_1000.py
if errorlevel 1 goto end

echo Batch complete. Waiting 5 seconds before next batch...
timeout /t 5 /nobreak > nul
goto loop

:end
echo Enhancement process ended.
pause