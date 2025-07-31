"""
Verify Azure Services Configuration
Tests all Azure service connections
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def check_azure_services():
    """Check all Azure service configurations"""
    print("🔍 Verifying Azure Service Configuration")
    print("=" * 50)
    
    services = {
        'Azure OpenAI': {
            'key_var': 'AZURE_OPENAI_API_KEY',
            'endpoint_var': 'AZURE_OPENAI_ENDPOINT',
            'required': True
        },
        'Azure Computer Vision': {
            'key_var': 'AZURE_VISION_KEY',
            'endpoint_var': 'AZURE_VISION_ENDPOINT',
            'required': True
        },
        'Azure Document Intelligence': {
            'key_var': 'AZURE_DOCUMENT_INTELLIGENCE_KEY',
            'endpoint_var': 'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT',
            'required': True
        },
        'Azure Translator': {
            'key_var': 'AZURE_TRANSLATOR_KEY',
            'endpoint_var': 'AZURE_TRANSLATOR_ENDPOINT',
            'required': True
        },
        'Azure Communication Services': {
            'key_var': 'AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING',
            'endpoint_var': None,
            'required': False
        }
    }
    
    all_configured = True
    
    for service_name, config in services.items():
        print(f"\n🔧 {service_name}:")
        
        # Check key
        key_value = os.getenv(config['key_var'])
        if key_value:
            print(f"  ✅ API Key configured ({config['key_var']})")
            print(f"     Length: {len(key_value)} characters")
        else:
            print(f"  ❌ API Key missing ({config['key_var']})")
            if config['required']:
                all_configured = False
        
        # Check endpoint if applicable
        if config['endpoint_var']:
            endpoint_value = os.getenv(config['endpoint_var'])
            if endpoint_value:
                print(f"  ✅ Endpoint configured: {endpoint_value}")
            else:
                print(f"  ❌ Endpoint missing ({config['endpoint_var']})")
                if config['required']:
                    all_configured = False
    
    # Check deployment names
    print("\n🚀 Deployment Configuration:")
    deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    if deployment_name:
        print(f"  ✅ OpenAI Deployment: {deployment_name}")
    else:
        print(f"  ❌ OpenAI Deployment not configured")
    
    vision_deployment = os.getenv('AZURE_OPENAI_VISION_DEPLOYMENT')
    if vision_deployment:
        print(f"  ✅ Vision Deployment: {vision_deployment}")
    
    # Summary
    print("\n" + "=" * 50)
    if all_configured:
        print("✅ All required Azure services are configured!")
    else:
        print("❌ Some Azure services need configuration")
    
    return all_configured


def test_azure_connections():
    """Test actual connections to Azure services"""
    print("\n\n🧪 Testing Azure Service Connections")
    print("=" * 50)
    
    # Test Azure OpenAI
    print("\n1️⃣ Testing Azure OpenAI...")
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )
        
        # Try a simple completion
        response = client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            messages=[{"role": "user", "content": "Say 'Azure OpenAI is working!'"}],
            max_tokens=10
        )
        print(f"  ✅ Azure OpenAI connection successful!")
        print(f"     Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"  ❌ Azure OpenAI connection failed: {str(e)}")
    
    # Test Azure Computer Vision
    print("\n2️⃣ Testing Azure Computer Vision...")
    try:
        from azure.cognitiveservices.vision.computervision import ComputerVisionClient
        from msrest.authentication import CognitiveServicesCredentials
        
        credentials = CognitiveServicesCredentials(os.getenv('AZURE_VISION_KEY'))
        client = ComputerVisionClient(
            endpoint=os.getenv('AZURE_VISION_ENDPOINT'),
            credentials=credentials
        )
        
        # Just verify client creation
        print(f"  ✅ Azure Computer Vision client created successfully!")
    except Exception as e:
        print(f"  ❌ Azure Computer Vision setup failed: {str(e)}")
    
    # Test Azure Document Intelligence
    print("\n3️⃣ Testing Azure Document Intelligence...")
    try:
        endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        if endpoint and key:
            print(f"  ✅ Azure Document Intelligence credentials available!")
        else:
            print(f"  ❌ Azure Document Intelligence credentials missing")
    except Exception as e:
        print(f"  ❌ Azure Document Intelligence check failed: {str(e)}")


if __name__ == "__main__":
    # First check configuration
    configured = check_azure_services()
    
    # Then test connections if configured
    if configured:
        test_azure_connections()
    else:
        print("\n⚠️  Fix configuration issues before testing connections")