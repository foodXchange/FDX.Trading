#!/bin/bash

# Bash script to deploy Azure resources for FoodXchange

# Default values
RESOURCE_GROUP="${RESOURCE_GROUP:-foodxchange-rg}"
LOCATION="${LOCATION:-eastus}"
OPENAI_LOCATION="${OPENAI_LOCATION:-eastus}"
PROJECT_NAME="${PROJECT_NAME:-foodxchange}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying Azure resources for FoodXchange...${NC}"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Please login to Azure...${NC}"
    az login
fi

# Create resource group if it doesn't exist
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    echo -e "${YELLOW}Creating resource group: $RESOURCE_GROUP in $LOCATION${NC}"
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
else
    echo -e "${GREEN}Using existing resource group: $RESOURCE_GROUP${NC}"
fi

# Deploy main resources
echo -e "\n${YELLOW}Deploying Azure resources...${NC}"
DEPLOYMENT_OUTPUT=$(az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "./azure/arm-templates/azure-resources.json" \
    --parameters projectName="$PROJECT_NAME" location="$LOCATION" openAiLocation="$OPENAI_LOCATION" \
    --query "properties.outputs" \
    -o json)

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Resources deployed successfully!${NC}"
    
    # Extract outputs
    STORAGE_ACCOUNT=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.storageAccountName.value')
    STORAGE_KEY=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.storageAccountKey.value')
    STORAGE_CONNECTION=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.storageConnectionString.value')
    DOC_INTEL_ENDPOINT=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.documentIntelligenceEndpoint.value')
    DOC_INTEL_KEY=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.documentIntelligenceKey.value')
    TRANSLATOR_ENDPOINT=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.translatorEndpoint.value')
    TRANSLATOR_KEY=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.translatorKey.value')
    OPENAI_ENDPOINT=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.openAiEndpoint.value')
    OPENAI_KEY=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.openAiKey.value')
    VISION_ENDPOINT=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.computerVisionEndpoint.value')
    VISION_KEY=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.computerVisionKey.value')
    
    # Display outputs
    echo -e "\n${CYAN}Resource Information:${NC}"
    echo "Storage Account: $STORAGE_ACCOUNT"
    echo "Document Intelligence Endpoint: $DOC_INTEL_ENDPOINT"
    echo "Translator Endpoint: $TRANSLATOR_ENDPOINT"
    echo "OpenAI Endpoint: $OPENAI_ENDPOINT"
    echo "Computer Vision Endpoint: $VISION_ENDPOINT"
    
    # Wait for OpenAI account to be ready
    echo -e "\n${YELLOW}Waiting for OpenAI account to be ready...${NC}"
    sleep 30
    
    # Deploy GPT-4 model
    echo -e "\n${YELLOW}Deploying GPT-4 model...${NC}"
    OPENAI_NAME="${PROJECT_NAME}-openai"
    
    az deployment group create \
        --resource-group "$RESOURCE_GROUP" \
        --template-file "./azure/arm-templates/gpt4-deployment.json" \
        --parameters openAiAccountName="$OPENAI_NAME"
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}GPT-4 deployment successful!${NC}"
        
        # Generate .env file
        echo -e "\n${YELLOW}Generating .env file...${NC}"
        
        # Generate a random secret key
        SECRET_KEY=$(openssl rand -hex 32)
        
        cat > .env << EOF
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION
AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT
AZURE_STORAGE_ACCOUNT_KEY=$STORAGE_KEY

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=$DOC_INTEL_ENDPOINT
AZURE_DOCUMENT_INTELLIGENCE_KEY=$DOC_INTEL_KEY

# Azure Translator
AZURE_TRANSLATOR_ENDPOINT=$TRANSLATOR_ENDPOINT
AZURE_TRANSLATOR_KEY=$TRANSLATOR_KEY
AZURE_TRANSLATOR_REGION=$LOCATION

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY=$OPENAI_KEY
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_VISION_DEPLOYMENT=gpt-4o

# Azure Computer Vision
AZURE_VISION_ENDPOINT=$VISION_ENDPOINT
AZURE_VISION_KEY=$VISION_KEY

# Application Settings
DATABASE_URL=sqlite:///./foodxchange.db
SECRET_KEY=$SECRET_KEY
ENVIRONMENT=development
EOF
        
        echo -e "${GREEN}.env file created successfully!${NC}"
        
        echo -e "\n${CYAN}Deployment complete! Next steps:${NC}"
        echo "1. Review the .env file and update any values as needed"
        echo "2. Run 'python foodxchange/main.py' to start the application"
        echo "3. The AI-powered import features are now ready to use!"
        
    else
        echo -e "${RED}GPT-4 deployment failed. Please check the error messages.${NC}"
        exit 1
    fi
else
    echo -e "${RED}Resource deployment failed. Please check the error messages.${NC}"
    exit 1
fi