#!/usr/bin/env pwsh
# Fixed Azure Deployment Script for FoodXchange

Write-Host "=== Fixed Azure Deployment for FoodXchange ===" -ForegroundColor Green

# Set variables for correct environment
$RESOURCE_GROUP = "foodxchange-deploy"
$ACR_NAME = "foodxchangeacr2025deploy"
$APP_NAME = "foodxchange-deploy-app"
$IMAGE_NAME = "foodxchange-web"
$IMAGE_TAG = "latest"

Write-Host "Checking Azure login..." -ForegroundColor Yellow
try {
    $currentUser = az account show --query user.name -o tsv
    Write-Host "Logged in as: $currentUser" -ForegroundColor Green
} catch {
    Write-Host "Please login to Azure first: az login" -ForegroundColor Red
    exit 1
}

Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Logging into Azure Container Registry..." -ForegroundColor Yellow
az acr login --name $ACR_NAME
if ($LASTEXITCODE -ne 0) {
    Write-Host "ACR login failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Tagging image for ACR..." -ForegroundColor Yellow
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}

Write-Host "Pushing image to ACR..." -ForegroundColor Yellow
docker push ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Updating App Service..." -ForegroundColor Yellow
az webapp config container set `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --docker-custom-image-name ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} `
    --docker-registry-server-url https://${ACR_NAME}.azurecr.io

if ($LASTEXITCODE -ne 0) {
    Write-Host "App Service update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Restarting App Service..." -ForegroundColor Yellow
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

Write-Host "=== Deployment Complete ===" -ForegroundColor Green
Write-Host "App URL: https://$APP_NAME.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP" -ForegroundColor Cyan