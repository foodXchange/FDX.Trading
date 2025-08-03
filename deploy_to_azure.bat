@echo off
echo ========================================
echo Deploy FoodXchange to Azure App Service
echo ========================================
echo.

echo 🔧 Setting up Azure deployment...
echo.

echo 📋 Prerequisites:
echo 1. Azure CLI installed
echo 2. Azure account with subscription
echo 3. Azure App Service plan
echo.

echo 🔐 Login to Azure:
echo az login
echo.

echo 📦 Deploy to Azure App Service:
echo az webapp up --name foodxchange-app --resource-group foodxchange-rg --runtime "PYTHON:3.11"
echo.

echo 🌐 Your app will be available at:
echo https://foodxchange-app.azurewebsites.net
echo.

echo 📋 Environment Variables to set in Azure:
echo DATABASE_URL=postgresql://your-admin@your-server.postgres.database.azure.com:5432/foodxchange_db
echo DEBUG=False
echo SECRET_KEY=your-secret-key-here
echo.

pause 