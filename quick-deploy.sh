#!/bin/bash
# Bash script for ultra-fast Azure deployment
# Run: ./quick-deploy.sh

echo "🚀 Quick Deploy to Azure"

# Create deployment package (exclude unnecessary files)
echo "📦 Creating deployment package..."
zip -r deploy.zip foodxchange main.py requirements.txt startup.sh web.config runtime.txt \
    -x "*.pyc" "*__pycache__*" "*.git*" "*.env" "venv/*" "*.log"

# Deploy to Azure
echo "☁️ Deploying to Azure..."
az webapp deployment source config-zip \
    --resource-group foodxchange-rg \
    --name foodxchange-app \
    --src deploy.zip

# Check deployment status
echo "✅ Deployment complete!"
echo "📊 Checking app status..."
az webapp show --name foodxchange-app --resource-group foodxchange-rg --query state -o tsv

# Tail logs
echo "📜 Tailing logs (Ctrl+C to stop)..."
az webapp log tail --name foodxchange-app --resource-group foodxchange-rg