@echo off
echo Checking DNS propagation using Google DNS (8.8.8.8)...
echo.

echo Checking A record (root domain):
nslookup foodxchange.com 8.8.8.8
echo.

echo Checking CNAME record (www subdomain):
nslookup www.foodxchange.com 8.8.8.8
echo.

echo Checking TXT record for Azure verification:
nslookup -type=txt foodxchange.com 8.8.8.8
echo.

echo If Google DNS shows the correct IP (20.105.232.36), then propagation is happening.
echo Your local DNS will update soon.
pause 