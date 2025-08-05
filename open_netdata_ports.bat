@echo off
echo ========================================
echo Opening Netdata Ports in Azure
echo ========================================
echo.

REM Open port 3000
echo Opening port 3000 for Netdata Web UI...
az network nsg rule create --resource-group fdx-resources --nsg-name fdx-vm-nsg --name Allow-Netdata-3000 --priority 1030 --direction Inbound --access Allow --protocol Tcp --source-address-prefixes "*" --source-port-ranges "*" --destination-address-prefixes "*" --destination-port-ranges 3000 --description "Allow Netdata on port 3000"

echo.
REM Open port 19999
echo Opening port 19999 for Netdata API...
az network nsg rule create --resource-group fdx-resources --nsg-name fdx-vm-nsg --name Allow-Netdata-19999 --priority 1031 --direction Inbound --access Allow --protocol Tcp --source-address-prefixes "*" --source-port-ranges "*" --destination-address-prefixes "*" --destination-port-ranges 19999 --description "Allow Netdata on port 19999"

echo.
echo ========================================
echo Ports opened successfully!
echo ========================================
echo.
echo Netdata should be accessible at:
echo   - http://4.206.1.15:3000  (Web UI)
echo   - http://4.206.1.15:19999 (API)
echo.
pause