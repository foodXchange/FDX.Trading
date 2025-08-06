#!/bin/bash

# FoodXchange GitHub Secrets Setup Script
# Poland Central Infrastructure

echo "🔧 Setting up GitHub Secrets for FoodXchange"
echo "📍 Poland Central VM: 74.248.141.31"
echo ""

# Get repository name
REPO=$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')
echo "📦 Repository: $REPO"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Please run:"
    echo "   gh auth login"
    exit 1
fi

echo "✅ GitHub CLI ready"
echo ""

# Database Configuration
echo "🗄️ Database Configuration:"
echo "1. DATABASE_URL - PostgreSQL connection string"
echo "   gh secret set DATABASE_URL --body 'postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require' --repo $REPO"
echo ""

# VM Configuration
echo "🖥️ VM Configuration:"
echo "2. VM_SSH_KEY - SSH private key for VM access"
echo "   gh secret set VM_SSH_KEY --body '$(cat ~/.ssh/fdx_poland_key)' --repo $REPO"
echo ""

# Azure OpenAI Configuration
echo "🤖 Azure OpenAI Configuration:"
echo "3. AZURE_OPENAI_KEY - Your Azure OpenAI API key"
echo "   gh secret set AZURE_OPENAI_KEY --body 'YOUR_KEY' --repo $REPO"
echo ""
echo "4. AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint"
echo "   gh secret set AZURE_OPENAI_ENDPOINT --body 'https://YOUR_RESOURCE.openai.azure.com/' --repo $REPO"
echo ""
echo "5. AZURE_OPENAI_DEPLOYMENT - Your deployment name (e.g., gpt-4o-mini)"
echo "   gh secret set AZURE_OPENAI_DEPLOYMENT --body 'gpt-4o-mini' --repo $REPO"
echo ""

# Environment Variables
echo "🌍 Environment Variables:"
echo "6. VM_HOST - VM IP address"
echo "   gh secret set VM_HOST --body '74.248.141.31' --repo $REPO"
echo ""
echo "7. VM_USER - VM username"
echo "   gh secret set VM_USER --body 'azureuser' --repo $REPO"
echo ""

# Optional: Email Configuration
echo "📧 Optional Email Configuration:"
echo "8. SMTP_SERVER - SMTP server for email notifications"
echo "   gh secret set SMTP_SERVER --body 'smtp-mail.outlook.com' --repo $REPO"
echo ""
echo "9. SMTP_PORT - SMTP port"
echo "   gh secret set SMTP_PORT --body '587' --repo $REPO"
echo ""
echo "10. SMTP_USERNAME - SMTP username"
echo "    gh secret set SMTP_USERNAME --body 'your-email@domain.com' --repo $REPO"
echo ""
echo "11. SMTP_PASSWORD - SMTP password"
echo "    gh secret set SMTP_PASSWORD --body 'your-password' --repo $REPO"
echo ""

echo "🚀 Ready to set secrets!"
echo ""
echo "💡 Tips:"
echo "- Replace 'YOUR_KEY' with actual values"
echo "- Use environment variables for sensitive data"
echo "- Test deployment after setting secrets"
echo ""
echo "🔗 VM Details:"
echo "- IP: 74.248.141.31"
echo "- Location: Poland Central"
echo "- Performance: 30ms latency from Israel"
echo "- Cost: $57/month"
echo ""
echo "📋 Next Steps:"
echo "1. Run the commands above to set secrets"
echo "2. Test deployment with: gh workflow run deploy.yml"
echo "3. Monitor deployment in GitHub Actions"
echo "4. Check application at: http://74.248.141.31"