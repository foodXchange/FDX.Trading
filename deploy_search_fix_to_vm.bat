@echo off
echo ========================================
echo Deploying Fixed Search to Azure VM
echo ========================================
echo.

echo Step 1: Uploading fixed search files to VM...
scp -i C:\Users\foodz\.ssh\fdx-vm-key.pem fixed_search_system.py azureuser@4.206.1.15:~/foodxchange/
scp -i C:\Users\foodz\.ssh\fdx-vm-key.pem app.py azureuser@4.206.1.15:~/foodxchange/

echo.
echo Step 2: Restarting the application on VM...
ssh -i C:\Users\foodz\.ssh\fdx-vm-key.pem azureuser@4.206.1.15 "cd ~/foodxchange && pkill -f 'python3.*app.py' && nohup python3 app.py > app.log 2>&1 &"

echo.
echo Step 3: Checking if app is running...
timeout /t 5 /nobreak > nul
ssh -i C:\Users\foodz\.ssh\fdx-vm-key.pem azureuser@4.206.1.15 "ps aux | grep 'python3.*app.py' | grep -v grep"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Test the search at: http://4.206.1.15:8000/suppliers
echo.
pause