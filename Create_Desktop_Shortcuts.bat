@echo off
echo Creating Desktop Shortcuts for VM Access...

set DESKTOP=%USERPROFILE%\Desktop
set CURRENT_DIR=%~dp0

REM Create VM Access shortcut
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\VM Access.lnk'); $Shortcut.TargetPath = '%CURRENT_DIR%VM_ACCESS.bat'; $Shortcut.IconLocation = 'C:\Windows\System32\imageres.dll,15'; $Shortcut.Description = 'FDX VM Control Center'; $Shortcut.Save()"

REM Create Monitoring shortcut
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\VM Monitoring.lnk'); $Shortcut.TargetPath = '%CURRENT_DIR%MONITORING.bat'; $Shortcut.IconLocation = 'C:\Windows\System32\imageres.dll,3'; $Shortcut.Description = 'Grafana and Netdata Access'; $Shortcut.Save()"

REM Create Netdata Direct shortcut
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Netdata.lnk'); $Shortcut.TargetPath = '%CURRENT_DIR%netdata_access.bat'; $Shortcut.IconLocation = 'C:\Windows\System32\imageres.dll,11'; $Shortcut.Description = 'Netdata Real-time Monitoring'; $Shortcut.Save()"

REM Create Quick Dashboard shortcut
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\VM Dashboard.lnk'); $Shortcut.TargetPath = '%CURRENT_DIR%quick_vm_access.html'; $Shortcut.IconLocation = 'C:\Windows\System32\imageres.dll,18'; $Shortcut.Description = 'VM Quick Access Dashboard'; $Shortcut.Save()"

echo.
echo ✅ Desktop shortcuts created successfully!
echo.
echo You now have 4 shortcuts on your desktop:
echo.
echo 1. VM Access - Main control center
echo 2. VM Monitoring - Grafana + Netdata
echo 3. Netdata - Direct Netdata access
echo 4. VM Dashboard - HTML quick access
echo.
pause