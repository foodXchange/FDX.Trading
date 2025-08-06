#!/usr/bin/env python3
import os

print("Updating VM configuration...")

# New configuration
new_env_content = """# FDX Trading Environment Configuration

# Database - New Managed PostgreSQL
DATABASE_URL=postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require

# Azure OpenAI Configuration
AZURE_OPENAI_KEY=4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# User Email
USER_EMAIL=udi@fdx.trading

# Other configurations can be added here
"""

# Backup existing .env
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        backup = f.read()
    with open('.env.backup', 'w') as f:
        f.write(backup)
    print("Backed up existing .env to .env.backup")

# Write new .env
with open('.env', 'w') as f:
    f.write(new_env_content)

print("Updated .env file with new configuration")
print("\nNew configuration includes:")
print("- New managed PostgreSQL database")
print("- Azure OpenAI credentials")
print("\nRestart the app with: sudo systemctl restart fdx-app")
