@echo off
echo ======================================
echo Upload Excel File to VM
echo ======================================
echo.
echo This will upload the suppliers Excel file to the VM
echo.

echo Uploading to azureuser home directory...
scp "C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx" azureuser@4.206.1.15:~/
echo.
echo If prompted for password, enter: FDX2025!Import#VM
echo.
echo File will be uploaded to: /home/azureuser/Suppliers 29_7_2025.xlsx
echo.
echo After upload, you can run the import script on the VM!
pause