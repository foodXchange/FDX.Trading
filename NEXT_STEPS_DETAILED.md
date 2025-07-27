# Detailed Next Steps for FoodXchange Azure Deployment

## Step 1: Configure Azure OpenAI Settings

### 1.1 Access Azure Portal
1. Open your browser and go to: https://portal.azure.com
2. Sign in with your Azure account

### 1.2 Navigate to Your App
1. In the search bar at the top, type: `foodxchange-app`
2. Click on your app service from the results

### 1.3 Configure Application Settings
1. In the left sidebar, find "Settings" section
2. Click on **"Configuration"**
3. Click on **"Application settings"** tab
4. Click **"+ New application setting"** for each of these:

**Setting 1:**
- Name: `AZURE_OPENAI_ENDPOINT`
- Value: Your Azure OpenAI endpoint (e.g., `https://your-resource-name.openai.azure.com/`)
- Click OK

**Setting 2:**
- Name: `AZURE_OPENAI_API_KEY`
- Value: Your Azure OpenAI API key
- Click OK

**Setting 3:**
- Name: `AZURE_OPENAI_DEPLOYMENT_NAME`
- Value: Your model deployment name (e.g., `gpt-4o`)
- Click OK

**Setting 4:**
- Name: `AZURE_OPENAI_API_VERSION`
- Value: `2024-02-15-preview`
- Click OK

5. **IMPORTANT**: Click **"Save"** at the top of the page
6. Click **"Continue"** when prompted about restarting the app

### 1.4 Where to Find Your Azure OpenAI Credentials
1. Go to Azure Portal home
2. Search for "Azure OpenAI"
3. Click on your Azure OpenAI resource
4. In the left sidebar:
   - Click **"Keys and Endpoint"** to find your API key and endpoint
   - Click **"Model deployments"** to find your deployment name

## Step 2: Set Up GitHub Actions for Continuous Deployment

### 2.1 Get the Publish Profile Content
1. Open PowerShell or Command Prompt
2. Navigate to your project: `cd C:\Users\foodz\Desktop\FoodXchange`
3. View the publish profile: `type publish_profile.xml`
4. Select ALL the XML content (Ctrl+A) and copy it (Ctrl+C)

### 2.2 Add to GitHub Secrets
1. Go to your GitHub repository: https://github.com/[your-username]/FoodXchange
2. Click on **"Settings"** tab (in the repository, not your profile)
3. In the left sidebar, scroll down to **"Secrets and variables"**
4. Click on **"Actions"**
5. Click **"New repository secret"** button
6. Fill in:
   - Name: `AZUREAPPSERVICE_PUBLISHPROFILE`
   - Secret: Paste the XML content you copied
7. Click **"Add secret"**

### 2.3 Enable GitHub Actions
1. Go to the **"Actions"** tab in your repository
2. You should see the workflow "Deploy to Azure Web App with Publish Profile"
3. If you see a message about workflows being disabled, click **"I understand my workflows, go ahead and enable them"**

## Step 3: Verify Your Deployment

### 3.1 Check Application Health
1. Open your browser
2. Go to: https://foodxchange-app.azurewebsites.net/health
3. You should see a JSON response indicating the app is healthy

### 3.2 Check System Status
1. Go to: https://foodxchange-app.azurewebsites.net/system-status
2. This page shows detailed system information

### 3.3 Access Your Main Application
1. Go to: https://www.fdx.trading or https://foodxchange-app.azurewebsites.net
2. You should see your FoodXchange application

## Step 4: Monitor Your Application

### 4.1 View Live Logs
Open PowerShell and run:
```bash
az webapp log tail --name foodxchange-app --resource-group foodxchange-rg
```
Press Ctrl+C to stop viewing logs

### 4.2 Check Deployment Logs in Azure Portal
1. In Azure Portal, go to your app service
2. In the left sidebar, under "Deployment", click **"Deployment Center"**
3. Click on **"Logs"** tab to see deployment history

### 4.3 Enable Application Insights (Optional but Recommended)
1. In your app service, click **"Application Insights"** in the left sidebar
2. Click **"Turn on Application Insights"**
3. Create a new resource or use existing
4. Click **"Apply"**

## Step 5: Test Azure OpenAI Integration

### 5.1 Test AI Features
1. Once you've configured the OpenAI settings, restart your app:
   - In Azure Portal, go to your app service
   - Click **"Restart"** in the top menu
   - Wait 2-3 minutes

2. Test the AI endpoint:
   - Go to: https://foodxchange-app.azurewebsites.net/test-ai
   - You should see the AI test interface

## Troubleshooting Common Issues

### If the app doesn't load:
1. Check the logs: `az webapp log tail --name foodxchange-app --resource-group foodxchange-rg`
2. Verify all environment variables are set correctly
3. Ensure the deployment completed successfully

### If AI features don't work:
1. Double-check your Azure OpenAI credentials
2. Ensure your Azure OpenAI resource has the gpt-4o model deployed
3. Check that the API version matches your deployment

### If you see authentication errors:
1. Verify your SECRET_KEY is set in Application Settings
2. Clear your browser cookies for the domain
3. Try accessing in an incognito/private browser window

## Next Development Steps

1. **Set up a proper database**: Consider migrating from SQLite to Azure SQL Database
2. **Configure custom domain DNS**: Ensure www.fdx.trading points to your app
3. **Set up SSL certificates**: If not already configured
4. **Configure backup**: Set up automated backups for your app
5. **Set up staging slots**: For testing before production deployments

## Support Resources

- Azure App Service Documentation: https://docs.microsoft.com/en-us/azure/app-service/
- Azure OpenAI Documentation: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/
- GitHub Actions Documentation: https://docs.github.com/en/actions

Remember to keep your API keys secure and never commit them to your repository!