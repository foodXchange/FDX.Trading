#!/bin/bash
# Configure App Services to use Key Vault references

RESOURCE_GROUP="rg-foodxchange"
KEY_VAULT_NAME="kv-foodxchange"
API_APP="app-foodxchange-api"
WEB_APP="app-foodxchange-web"

echo "Configuring App Services with Key Vault references..."

# Configure API App Service
echo "Configuring API App Service..."

# Azure OpenAI settings with Key Vault references
az webapp config appsettings set \
  -g $RESOURCE_GROUP \
  -n $API_APP \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://openai-foodxchange.openai.azure.com/" \
    AZURE_OPENAI_KEY="@Microsoft.KeyVault(VaultName=$KEY_VAULT_NAME;SecretName=AzureOpenAIKey)" \
    AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini" \
    APPLICATIONINSIGHTS_CONNECTION_STRING="@Microsoft.KeyVault(VaultName=$KEY_VAULT_NAME;SecretName=ApplicationInsightsConnection)"

# SQL Connection with Managed Identity (no Key Vault needed)
az webapp config connection-string set \
  -g $RESOURCE_GROUP \
  -n $API_APP \
  --connection-string-type SQLAzure \
  --settings Sql="Server=tcp:sql-foodxchange.database.windows.net,1433;Database=FoodXchange;Authentication=Active Directory Managed Identity;Encrypt=True;TrustServerCertificate=False;"

# Configure Web App
echo "Configuring Web App..."

az webapp config appsettings set \
  -g $RESOURCE_GROUP \
  -n $WEB_APP \
  --settings \
    ApiBaseUrl="https://$API_APP.azurewebsites.net/" \
    APPLICATIONINSIGHTS_CONNECTION_STRING="@Microsoft.KeyVault(VaultName=$KEY_VAULT_NAME;SecretName=ApplicationInsightsConnection)"

echo "Configuration complete!"
echo ""
echo "Key Vault references syntax:"
echo "  @Microsoft.KeyVault(VaultName=$KEY_VAULT_NAME;SecretName=SecretName)"
echo ""
echo "To verify:"
echo "  1. Check https://$API_APP.azurewebsites.net/health"
echo "  2. Check https://$API_APP.azurewebsites.net/db/verify"
echo "  3. Visit https://$WEB_APP.azurewebsites.net/admin/diagnostics"