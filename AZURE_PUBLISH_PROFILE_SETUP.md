# Azure Publish Profile Setup for GitHub Actions

## Quick Setup (Recommended)

### Option 1: Using Azure Portal (Easiest)

1. **Get Publish Profile:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to your Web App (foodxchange-app)
   - Click "Get publish profile" button
   - Download the `.PublishSettings` file
   - Open the file in a text editor
   - Copy the entire content

2. **Add to GitHub Secrets:**
   - Go to your GitHub repository
   - Click Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `AZUREAPPSERVICE_PUBLISHPROFILE`
   - Value: Paste the entire publish profile content
   - Click "Add secret"

3. **Deploy:**
   - Push your code to the `main` branch
   - The workflow will automatically trigger

### Option 2: Using Azure CLI

```powershell
# Login to Azure
az login

# Get publish profile
az webapp deployment list-publishing-profiles --name foodxchange-app --resource-group your-resource-group --output json
```

## Workflow Files

You have two options:

### Simple Deployment (Recommended)
Use: `.github/workflows/deploy_simple_publish_profile.yml`
- Only requires publish profile
- No Azure login needed
- Simpler setup

### Full Deployment with Azure Login
Use: `.github/workflows/deploy_with_publish_profile.yml`
- Requires both publish profile and Azure credentials
- More secure but complex setup
- Use the `setup_azure_github_secrets.ps1` script

## Troubleshooting

### Error: "No credentials found"
- Make sure you're using the simple workflow OR
- Add Azure login step with proper credentials

### Error: "Invalid publish profile"
- Download a fresh publish profile from Azure Portal
- Make sure the entire content is copied (including XML tags)

### Error: "App not found"
- Verify the app name in the workflow matches your Azure Web App name
- Check that the publish profile is for the correct app

## Security Notes

- Never commit publish profiles to your repository
- Publish profiles contain sensitive information
- Rotate publish profiles periodically
- Use repository secrets to store sensitive data

## Next Steps

1. Choose your preferred workflow file
2. Get the publish profile from Azure Portal
3. Add it to GitHub secrets
4. Push your code to trigger deployment
5. Monitor the deployment in GitHub Actions tab 