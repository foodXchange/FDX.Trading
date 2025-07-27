# CI/CD Setup Guide for FoodXchange

## Overview

The FoodXchange application uses GitHub Actions for continuous integration and deployment to Azure App Service. This guide explains the setup and configuration.

## Current Configuration

### Main Workflow File
- **Location**: `.github/workflows/main_foodxchange-app.yml`
- **Triggers**: 
  - Push to main branch
  - Pull requests to main branch
  - Manual workflow dispatch

### Workflow Features

1. **Build Stage**:
   - Python 3.12 setup
   - Node.js 20.x setup
   - Dependency installation
   - Code linting (flake8)
   - Code formatting check (black)
   - Test execution (placeholder)
   - Optimized deployment package creation

2. **Deploy Stage**:
   - Multi-authentication support (OIDC, Service Principal, Publish Profile)
   - Automatic fallback mechanism
   - Post-deployment health check
   - Environment URL tracking

## Authentication Methods

The workflow supports three authentication methods with automatic fallback:

### 1. OIDC (Federated Credentials) - Most Secure
Required secrets:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

### 2. Service Principal - Traditional
Required secret:
- `AZURE_CREDENTIALS` (JSON format)

### 3. Publish Profile - Simplest
Required secret:
- `AZUREAPPSERVICE_PUBLISHPROFILE`

## Quick Setup

### Step 1: Configure GitHub Secrets

Run the provided PowerShell script:
```powershell
.\setup-github-secrets.ps1
```

Or manually add secrets in GitHub:
1. Go to Settings > Secrets and variables > Actions
2. Add required secrets based on your chosen authentication method

### Step 2: Get Azure Credentials

#### For Publish Profile (Recommended for quick setup):
1. Go to Azure Portal
2. Navigate to your App Service (foodxchange-app)
3. Click "Download publish profile"
4. Copy the entire file contents as the secret value

#### For OIDC:
1. Create an App Registration in Azure AD
2. Configure federated credentials for GitHub
3. Note the Client ID, Tenant ID, and Subscription ID

#### For Service Principal:
```bash
az ad sp create-for-rbac --name "github-actions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/foodxchange-rg \
  --sdk-auth
```

### Step 3: Verify Setup

1. Push changes to main branch
2. Check Actions tab in GitHub
3. Monitor deployment progress

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify secret names match exactly
   - Check secret values don't have extra spaces
   - Ensure proper permissions in Azure

2. **Build Failures**
   - Check requirements.txt is up to date
   - Verify Python version compatibility
   - Review linting errors in logs

3. **Deployment Failures**
   - Confirm App Service is running
   - Check resource group name is correct
   - Verify app name matches configuration

### Useful Commands

```bash
# View workflow runs
gh run list

# View specific run details
gh run view <run-id>

# Re-run failed workflow
gh run rerun <run-id>

# View secrets (names only)
gh secret list

# Update a secret
echo "new-value" | gh secret set SECRET_NAME
```

## Archived Workflows

Previous workflow files have been archived to `.github/workflows/archive/`:
- `deploy_simple.yml`
- `deploy_simple_publish_profile.yml`
- `deploy_with_migrations.yml`
- `deploy_with_publish_profile.yml`

## Best Practices

1. **Security**:
   - Use OIDC when possible for enhanced security
   - Rotate credentials regularly
   - Never commit secrets to repository

2. **Performance**:
   - Workflow caches dependencies
   - Parallel job execution where possible
   - Optimized deployment package excludes unnecessary files

3. **Monitoring**:
   - Health check after deployment
   - Environment URLs for easy access
   - Detailed logging for troubleshooting

## Next Steps

1. Set up branch protection rules
2. Configure deployment environments
3. Add comprehensive test suite
4. Set up deployment notifications

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure App Service Deploy Action](https://github.com/Azure/webapps-deploy)
- [Azure Login Action](https://github.com/Azure/login)