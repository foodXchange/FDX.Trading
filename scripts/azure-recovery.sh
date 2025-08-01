#!/bin/bash
# Azure FoodXchange Recovery Script (Bash version)
# This script restores the last known working configuration

echo -e "\033[32mAzure FoodXchange Recovery Script\033[0m"
echo -e "\033[32m=================================\033[0m"

# Configuration
RESOURCE_GROUP="foodxchange-deploy"
WEBAPP_NAME="foodxchange-deploy-app"
WORKING_IMAGE="foodxchangeacr2025deploy.azurecr.io/foodxchange:8e3c88b4e8b4b9763711f850cf917d22e786c09e"
WEBSITES_PORT="9000"

echo -e "\n\033[33mStep 1: Checking current status...\033[0m"
az webapp show --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP --query "{state:state, health:healthCheckPath}" -o table

echo -e "\n\033[33mStep 2: Setting container to last known working image...\033[0m"
az webapp config container set \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $WORKING_IMAGE

echo -e "\n\033[33mStep 3: Setting correct port configuration...\033[0m"
az webapp config appsettings set \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings WEBSITES_PORT=$WEBSITES_PORT PORT=$WEBSITES_PORT

echo -e "\n\033[33mStep 4: Setting production environment variables...\033[0m"
az webapp config appsettings set \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    ENVIRONMENT=production \
    DEBUG=False \
    DOMAIN=fdx.trading \
    BASE_URL=https://www.fdx.trading

echo -e "\n\033[33mStep 5: Restarting the web app...\033[0m"
az webapp restart --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP

echo -e "\n\033[33mStep 6: Waiting for app to start (90 seconds)...\033[0m"
sleep 90

echo -e "\n\033[33mStep 7: Testing site availability...\033[0m"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://www.fdx.trading/)
if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "\033[32m✅ Site is responding correctly!\033[0m"
else
    echo -e "\033[31m❌ Site is not responding (HTTP $HTTP_STATUS). Check logs with:\033[0m"
    echo -e "\033[33maz webapp log tail --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP\033[0m"
fi

echo -e "\n\033[32mRecovery script completed.\033[0m"