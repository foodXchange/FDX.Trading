@echo off
REM Install Azure CLI on Windows
REM This script installs Azure CLI using the MSI installer

echo Installing Azure CLI...
echo.

REM Download and install Azure CLI
echo Downloading Azure CLI installer...
powershell -Command "Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi"

echo Installing Azure CLI...
msiexec.exe /i AzureCLI.msi /quiet

echo.
echo Azure CLI installation complete!
echo.
echo To verify installation, run: az --version
echo To login to Azure, run: az login
echo.
pause