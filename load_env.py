import os
from dotenv import load_dotenv

# Load main .env file
load_dotenv('.env')

# Load blob storage config from .env.blob
load_dotenv('.env.blob')

# Print loaded environment variables for debugging
print("Environment variables loaded:")
print(f"AZURE_OPENAI_API_KEY: {'***' + os.getenv('AZURE_OPENAI_API_KEY', '')[-4:] if os.getenv('AZURE_OPENAI_API_KEY') else 'Not set'}")
print(f"AZURE_STORAGE_CONNECTION_STRING: {'Set' if os.getenv('AZURE_STORAGE_CONNECTION_STRING') else 'Not set'}")
print(f"DATABASE_URL: {'Set' if os.getenv('DATABASE_URL') else 'Not set'}")