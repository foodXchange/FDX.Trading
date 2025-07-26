@echo off
echo Opening Azure Portal to configure firewall...
echo.
echo Your current IP: 85.65.236.169
echo.
echo Steps:
echo 1. Sign in to Azure Portal
echo 2. Your PostgreSQL server will open
echo 3. Click "Networking" in the left menu
echo 4. Click "+ Add current client IP address"
echo 5. Click "Save"
echo.
start https://portal.azure.com/#@/resource/subscriptions/[YOUR_SUBSCRIPTION_ID]/resourceGroups/FoodXchangeRG/providers/Microsoft.DBforPostgreSQL/flexibleServers/foodxchangepgfr/networking
echo.
echo If the direct link doesn't work, search for "foodxchangepgfr" in Azure Portal
pause