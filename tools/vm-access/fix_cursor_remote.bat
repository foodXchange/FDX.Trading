@echo off
echo Fixing Cursor Remote Connection...

REM Create proper SSH config
echo Host fdx-vm > %USERPROFILE%\.ssh\config
echo     HostName 4.206.1.15 >> %USERPROFILE%\.ssh\config
echo     User fdxfounder >> %USERPROFILE%\.ssh\config
echo     IdentityFile ~/.ssh/fdx_founders_key >> %USERPROFILE%\.ssh\config
echo     StrictHostKeyChecking no >> %USERPROFILE%\.ssh\config
echo     UserKnownHostsFile /dev/null >> %USERPROFILE%\.ssh\config

echo SSH config updated.

REM Alternative: Use VS Code instead
echo.
echo If Cursor still doesn't work, try VS Code instead:
echo 1. Install VS Code if not installed
echo 2. Install "Remote - SSH" extension
echo 3. Connect to fdx-vm
echo.
echo Or use SSH directly:
echo ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
echo.
pause