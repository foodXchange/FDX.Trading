@echo off
echo ========================================
echo   FoodXchange fdx.trading Domain Fix
echo ========================================
echo.

echo This script will:
echo 1. Fix the Azure deployment
echo 2. Configure custom domains (fdx.trading and www.fdx.trading)
echo 3. Set up SSL certificates
echo 4. Test the domains
echo.

echo Make sure you have:
echo - Azure CLI installed and logged in
echo - Namecheap domain fdx.trading ready
echo.

pause

echo.
echo Starting the fix...
python fix_fdx_trading_domain.py

echo.
echo ========================================
echo   Fix completed!
echo ========================================
echo.
echo Next steps:
echo 1. Configure DNS records in Namecheap (see NAMECHEAP_DNS_SETUP.md)
echo 2. Wait for DNS propagation (15-60 minutes)
echo 3. Test your domain: https://fdx.trading
echo.

pause 