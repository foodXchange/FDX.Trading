@echo off
echo GitHub Authentication Setup
echo ==========================
echo.
echo You need to authenticate with GitHub CLI first.
echo.
echo Step 1: Run this command:
echo gh auth login
echo.
echo Step 2: Choose:
echo - GitHub.com
echo - HTTPS
echo - Login with a web browser
echo.
echo Step 3: Copy the one-time code shown and open the URL
echo.
echo After authentication, run setup-github-secrets.ps1
echo.
pause
gh auth login