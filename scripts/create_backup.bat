@echo off
REM Create complete system backup before cleanup
echo === FoodXchange System Backup ===
echo.

REM Set backup directory with timestamp
set BACKUP_DIR=backup_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir %BACKUP_DIR%

echo 1. Backing up database...
copy foodxchange.db %BACKUP_DIR%\foodxchange_backup.db

echo 2. Backing up configuration files...
copy .env %BACKUP_DIR%\.env.backup 2>nul
copy .env.* %BACKUP_DIR%\ 2>nul
xcopy /E /I configs %BACKUP_DIR%\configs 2>nul

echo 3. Backing up user data...
xcopy /E /I uploads %BACKUP_DIR%\uploads 2>nul
xcopy /E /I static %BACKUP_DIR%\static 2>nul

echo 4. Creating code archive...
git archive --format=zip HEAD > %BACKUP_DIR%\code_backup.zip

echo.
echo === Backup Complete ===
echo Backup saved to: %BACKUP_DIR%
echo.
pause