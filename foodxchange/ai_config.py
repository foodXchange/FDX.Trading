"""
Azure AI Services Configuration for Product Analysis
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Azure AI Services Configuration
AZURE_AI_CONFIG = {
    # Computer Vision for image analysis
    "COMPUTER_VISION": {
        "endpoint": os.getenv("AZURE_COMPUTER_VISION_ENDPOINT", "https://eastus.api.cognitive.microsoft.com/"),
        "key": os.getenv("AZURE_COMPUTER_VISION_KEY", ""),
        "api_version": "2023-10-01"
    },
    
    # OpenAI for product brief generation
    "OPENAI": {
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        "key": os.getenv("AZURE_OPENAI_KEY", ""),
        "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
        "api_version": "2023-12-01-preview"
    },
    
    # Storage for product images
    "STORAGE": {
        "connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
        "container_name": "product-images"
    },
    
    # Cognitive Search for product matching (to be added)
    "SEARCH": {
        "endpoint": os.getenv("AZURE_SEARCH_ENDPOINT", ""),
        "key": os.getenv("AZURE_SEARCH_KEY", ""),
        "index_name": "products"
    }
}

# Database tables for AI product analysis
AI_TABLES = {
    "product_analyses": "Stores AI analysis results",
    "product_briefs": "Generated product briefs",
    "product_images": "Image storage and metadata",
    "ai_insights": "AI-generated insights"
}