#!/usr/bin/env python3
"""Test all Azure services configuration"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_service(name, *env_vars):
    """Check if service environment variables are set"""
    configured = all(os.getenv(var) for var in env_vars)
    status = "[OK] Configured" if configured else "[X] Not configured"
    print(f"{name}: {status}")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if 'KEY' in var or 'CONNECTION_STRING' in var:
                masked = value[:10] + "..." + value[-4:] if len(value) > 14 else value
                print(f"  - {var}: {masked}")
            else:
                print(f"  - {var}: {value}")
        else:
            print(f"  - {var}: NOT SET")
    return configured

print("Azure Services Configuration Status")
print("=" * 50)

services_configured = 0
total_services = 0

# 1. Azure OpenAI
total_services += 1
if check_service("Azure OpenAI", 
                 "AZURE_OPENAI_ENDPOINT", 
                 "AZURE_OPENAI_API_KEY",
                 "AZURE_OPENAI_DEPLOYMENT_NAME"):
    services_configured += 1

print()

# 2. Azure Computer Vision
total_services += 1
if check_service("Azure Computer Vision",
                 "AZURE_VISION_ENDPOINT",
                 "AZURE_VISION_KEY"):
    services_configured += 1

print()

# 3. Azure Document Intelligence
total_services += 1
if check_service("Azure Document Intelligence",
                 "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT",
                 "AZURE_DOCUMENT_INTELLIGENCE_KEY"):
    services_configured += 1

print()

# 4. Azure Translator
total_services += 1
if check_service("Azure Translator",
                 "AZURE_TRANSLATOR_ENDPOINT",
                 "AZURE_TRANSLATOR_KEY",
                 "AZURE_TRANSLATOR_REGION"):
    services_configured += 1

print()

# 5. Azure Cognitive Search
total_services += 1
if check_service("Azure Cognitive Search",
                 "AZURE_SEARCH_ENDPOINT",
                 "AZURE_SEARCH_KEY",
                 "AZURE_SEARCH_INDEX"):
    services_configured += 1

print()

# 6. Azure Storage
total_services += 1
if check_service("Azure Storage",
                 "AZURE_STORAGE_CONNECTION_STRING",
                 "AZURE_STORAGE_CONTAINER"):
    services_configured += 1

print()

# 7. Azure Communication Services (Email)
total_services += 1
if check_service("Azure Communication Services",
                 "AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING",
                 "AZURE_EMAIL_SENDER_ADDRESS"):
    services_configured += 1

print()

# 8. Azure Email Service (alias)
total_services += 1
if check_service("Azure Email Service (alias)",
                 "AZURE_EMAIL_CONNECTION_STRING"):
    services_configured += 1

print()

# 9. Azure OpenAI Vision Deployment
total_services += 1
if check_service("Azure OpenAI Vision",
                 "AZURE_OPENAI_VISION_DEPLOYMENT"):
    services_configured += 1

print()

# 10. Azure Text Analytics
total_services += 1
if check_service("Azure Text Analytics",
                 "AZURE_TEXT_ANALYTICS_ENDPOINT",
                 "AZURE_TEXT_ANALYTICS_KEY"):
    services_configured += 1

print()

# Check for any other potential Azure services
print("Additional Azure Environment Variables:")
print("-" * 50)
all_vars = [var for var in os.environ if var.startswith('AZURE_')]
configured_vars = [
    "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT_NAME",
    "AZURE_VISION_ENDPOINT", "AZURE_VISION_KEY",
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "AZURE_DOCUMENT_INTELLIGENCE_KEY",
    "AZURE_TRANSLATOR_ENDPOINT", "AZURE_TRANSLATOR_KEY", "AZURE_TRANSLATOR_REGION",
    "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_KEY", "AZURE_SEARCH_INDEX",
    "AZURE_STORAGE_CONNECTION_STRING", "AZURE_STORAGE_CONTAINER",
    "AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING", "AZURE_EMAIL_SENDER_ADDRESS",
    "AZURE_EMAIL_CONNECTION_STRING", "AZURE_OPENAI_VISION_DEPLOYMENT",
    "AZURE_TEXT_ANALYTICS_ENDPOINT", "AZURE_TEXT_ANALYTICS_KEY"
]

additional_vars = [var for var in all_vars if var not in configured_vars]
if additional_vars:
    for var in additional_vars:
        value = os.getenv(var)
        masked = value[:10] + "..." + value[-4:] if len(value) > 14 else value
        print(f"  - {var}: {masked}")
else:
    print("  None found")

print()
print("=" * 50)
print(f"Summary: {services_configured}/{total_services} services configured")
print("=" * 50)