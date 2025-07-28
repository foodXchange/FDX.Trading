# Quick Start: GitHub Actions Deployment for FoodXchange

This is the simplest way to set up automated deployment to Azure.

## Prerequisites
- GitHub account
- Access to Azure Portal

## Step 1: Download Publish Profile (2 minutes)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **App Services** → **foodxchange-app**
3. Click **"Get publish profile"** button
4. Save the downloaded file (it's an XML file)

## Step 2: Create GitHub Repository (3 minutes)

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit with GitHub Actions"

# Create new repo at https://github.com/new
# Name: FoodXchange
# Then add remote:
git remote add origin https://github.com/YOUR_USERNAME/FoodXchange.git
git push -u origin main
```

## Step 3: Add GitHub Secret (2 minutes)

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add:
   - **Name**: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - **Value**: Copy and paste the ENTIRE content of the publish profile XML file
5. Click **"Add secret"**

## Step 4: Trigger Deployment (1 minute)

The deployment will start automatically when you push. To trigger manually:

1. Go to **Actions** tab in your repository
2. Click on **"Deploy to Azure App Service"**
3. Click **"Run workflow"** → **"Run workflow"**

## Step 5: Monitor Deployment (5-10 minutes)

1. Watch the workflow progress in the Actions tab
2. Once complete, check:
   - https://foodxchange-app.azurewebsites.net/health
   - https://www.fdx.trading/health

## If Deployment Fails

Check these common issues:

1. **Module Import Errors**: Ensure all dependencies are in requirements.txt
2. **Startup Timeout**: The app might need more time to start
3. **Port Binding**: Make sure the app uses the PORT environment variable

## Simplified Workflow File

If you have issues, use this minimal workflow:

```yaml
name: Simple Azure Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: foodxchange-app
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

## Total Time: ~15 minutes

That's it! Your app will now deploy automatically every time you push to GitHub.