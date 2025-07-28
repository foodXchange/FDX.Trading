"""
Load all environment variables from multiple .env files
This ensures Azure Blob Storage and other configurations are properly loaded
"""
import os
from dotenv import load_dotenv

def load_all_env_files():
    """Load environment variables from all .env files"""
    # Load main .env file
    if os.path.exists('.env'):
        load_dotenv('.env', override=True)
        print("Loaded .env")
    
    # Load blob storage configuration
    if os.path.exists('.env.blob'):
        load_dotenv('.env.blob', override=True)
        print("Loaded .env.blob")
    
    # Verify critical Azure configurations
    azure_configs = {
        'AZURE_STORAGE_CONNECTION_STRING': os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY'),
        'AZURE_EMAIL_CONNECTION_STRING': os.getenv('AZURE_EMAIL_CONNECTION_STRING')
    }
    
    for key, value in azure_configs.items():
        if value:
            print(f"[OK] {key} is configured")
        else:
            print(f"[MISSING] {key} is NOT configured")
    
    return azure_configs

# Load environment variables when this module is imported
load_all_env_files()