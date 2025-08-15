#!/bin/bash
# Configure FDX App Services with Azure Key Vault and Managed Identity

RESOURCE_GROUP="rg-foodxchange"
KEY_VAULT_NAME="kv-foodxchange"
API_APP="app-foodxchange-api"
WEB_APP="app-foodxchange-web"
SQL_SERVER="fdx-sql-prod"
SQL_DATABASE="fdxdb"

echo "Configuring FDX App Services..."

# Enable Managed Identity on API App
echo "Enabling Managed Identity on API App..."
API_IDENTITY=$(az webapp identity assign \
  -g $RESOURCE_GROUP \
  -n $API_APP \
  --query principalId \
  --output tsv)

echo "API App Identity: $API_IDENTITY"

# Grant Key Vault access to API App
echo "Granting Key Vault access to API App..."
az keyvault set-policy \
  --name $KEY_VAULT_NAME \
  --object-id $API_IDENTITY \
  --secret-permissions get list

# Configure API App Service with Key Vault references
echo "Configuring API App Service settings..."

# For production with Managed Identity (recommended)
az webapp config connection-string set \
  -g $RESOURCE_GROUP \
  -n $API_APP \
  --connection-string-type SQLAzure \
  --settings Sql="Server=tcp:$SQL_SERVER.database.windows.net,1433;Database=$SQL_DATABASE;Authentication=Active Directory Managed Identity;Encrypt=True;TrustServerCertificate=False;"

# Alternative: Use Key Vault for SQL password (if not using Managed Identity)
# az webapp config connection-string set \
#   -g $RESOURCE_GROUP \
#   -n $API_APP \
#   --connection-string-type SQLAzure \
#   --settings Sql="@Microsoft.KeyVault(VaultName=$KEY_VAULT_NAME;SecretName=SqlConnectionFull)"

# Set Key Vault name in app settings
az webapp config appsettings set \
  -g $RESOURCE_GROUP \
  -n $API_APP \
  --settings \
    KeyVaultName="$KEY_VAULT_NAME" \
    ASPNETCORE_ENVIRONMENT="Production"

# Grant SQL Database access to Managed Identity
echo ""
echo "IMPORTANT: Run this SQL command in Azure Data Studio as SQL admin:"
echo ""
echo "-- Connect to fdxdb database (not master!)"
echo "CREATE USER [$API_APP] FROM EXTERNAL PROVIDER;"
echo "ALTER ROLE db_datareader ADD MEMBER [$API_APP];"
echo "ALTER ROLE db_datawriter ADD MEMBER [$API_APP];"
echo "-- If app runs migrations:"
echo "-- ALTER ROLE db_ddladmin ADD MEMBER [$API_APP];"
echo ""

# Configure Web App (if exists)
if az webapp show -g $RESOURCE_GROUP -n $WEB_APP &>/dev/null; then
  echo "Configuring Web App..."
  
  WEB_IDENTITY=$(az webapp identity assign \
    -g $RESOURCE_GROUP \
    -n $WEB_APP \
    --query principalId \
    --output tsv)
  
  az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $WEB_IDENTITY \
    --secret-permissions get list
  
  az webapp config appsettings set \
    -g $RESOURCE_GROUP \
    -n $WEB_APP \
    --settings \
      ApiBaseUrl="https://$API_APP.azurewebsites.net/" \
      KeyVaultName="$KEY_VAULT_NAME" \
      ASPNETCORE_ENVIRONMENT="Production"
fi

echo ""
echo "Configuration complete!"
echo ""
echo "Test endpoints:"
echo "  https://$API_APP.azurewebsites.net/health"
echo "  https://$API_APP.azurewebsites.net/db/verify"
echo ""
echo "If using SQL password authentication instead of Managed Identity:"
echo "  Update the connection string to use Key Vault reference"
echo ""