# GitHub Actions Deployment Setup for FoodXchange

This guide will help you set up automated deployment to Azure using GitHub Actions.

## Prerequisites
- GitHub account
- Azure subscription with App Service created
- Git installed locally

## Step 1: Create GitHub Repository

```bash
# Initialize git repository (if not already done)
git init

# Create .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo ".env.backup" >> .gitignore
echo "venv/" >> .gitignore
echo "*.log" >> .gitignore
echo "*.zip" >> .gitignore
echo "deployment_contents/" >> .gitignore
echo "emergency_deployment/" >> .gitignore

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create repository on GitHub
# Go to https://github.com/new and create a new repository named "FoodXchange"

# Add remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/FoodXchange.git

# Push to GitHub
git push -u origin main
```

## Step 2: Get Azure Publish Profile

1. Go to Azure Portal (https://portal.azure.com)
2. Navigate to your App Service (foodxchange-app)
3. In the Overview page, click "Get publish profile" 
4. Save the downloaded file

## Step 3: Add GitHub Secret

1. Go to your GitHub repository
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
5. Value: Copy the entire content of the publish profile file
6. Click "Add secret"

## Step 4: Create Service Principal (Alternative Method)

If you prefer using Azure credentials instead of publish profile:

```bash
# Create service principal
az ad sp create-for-rbac --name "github-actions-foodxchange" --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/foodxchange-rg --sdk-auth

# Copy the JSON output and add as GitHub secret named AZURE_CREDENTIALS
```

## Step 5: Update Workflow (if using Service Principal)

Replace the deploy step in `.github/workflows/azure-deploy.yml`:

```yaml
- name: Login to Azure
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}
    
- name: Deploy to Azure Web App
  uses: azure/webapps-deploy@v2
  with:
    app-name: ${{ env.AZURE_WEBAPP_NAME }}
```

## Step 6: Configure App Service

Run this PowerShell script to ensure proper configuration:

```powershell
# Set Python version
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --linux-fx-version "PYTHON|3.12"

# Set startup command
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app.main:app"

# Enable logging
az webapp log config --resource-group foodxchange-rg --name foodxchange-app --application-logging filesystem --level verbose

# Set environment variables (already done)
```

## Step 7: Push and Deploy

```bash
# Add any changes
git add .
git commit -m "Add GitHub Actions workflow"

# Push to trigger deployment
git push origin main
```

## Step 8: Monitor Deployment

1. Go to your GitHub repository
2. Click on "Actions" tab
3. Watch the workflow run
4. Check the deployment at https://www.fdx.trading

## Troubleshooting

### If deployment fails:

1. Check GitHub Actions logs
2. Check Azure App Service logs:
   ```bash
   az webapp log tail --name foodxchange-app --resource-group foodxchange-rg
   ```

3. Access Kudu console:
   https://foodxchange-app.scm.azurewebsites.net

### Common Issues:

1. **Module not found**: Ensure all dependencies are in requirements.txt
2. **Port binding**: Make sure to use PORT environment variable
3. **Startup timeout**: Increase startup time in web.config

## Benefits of GitHub Actions

1. **Automatic deployments** on every push to main
2. **Build validation** before deployment
3. **Easy rollback** using Git
4. **Deployment history** in GitHub
5. **Integration with pull requests**

## Next Steps

1. Set up staging environment
2. Add automated tests
3. Configure branch protection rules
4. Set up deployment approvals