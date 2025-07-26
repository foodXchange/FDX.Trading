@echo off
echo Checking DNS propagation for foodxchange.com...
echo.

echo Checking A record (root domain):
nslookup foodxchange.com
echo.

echo Checking CNAME record (www subdomain):
nslookup www.foodxchange.com
echo.

echo Checking TXT record for Azure verification:
nslookup -type=txt foodxchange.com
echo.

echo If you see the correct IP (20.105.232.36) and CNAME pointing to foodxchange-app.azurewebsites.net,
echo and the TXT record with the Azure verification string, then DNS propagation is complete.
echo.
echo You can now go back to Azure Portal and click "Validate" again.
pause 