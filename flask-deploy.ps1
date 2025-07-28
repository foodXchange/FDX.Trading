# Flask deployment script
Write-Host "Deploying Flask app..." -ForegroundColor Yellow

# Create minimal Flask requirements
@"
flask==3.0.3
gunicorn==21.2.0
"@ | Set-Content requirements_flask.txt

# Create deployment package with Flask app
Compress-Archive -Path @(
    "app.py",
    "requirements_flask.txt",
    "runtime.txt"
) -DestinationPath flask_deploy.zip -Force

# Deploy
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path flask_deploy.zip --type zip

# Wait and test
Write-Host "Waiting for deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "Testing endpoint..." -ForegroundColor Yellow
curl -s https://foodxchange-app.azurewebsites.net/health