# FoodXchange AI Services Setup

## Overview
This document outlines the Azure AI services required for the FoodXchange product analysis and sourcing module.

## Required Azure Services

### 1. Azure Computer Vision
- **Purpose**: Analyze product images to extract information
- **Resource**: `foodxchange-vision` in `foodxchange-ai-rg`
- **Features Used**:
  - Image analysis
  - OCR for label reading
  - Object detection for product identification

### 2. Azure OpenAI
- **Purpose**: Generate product briefs and insights
- **Resource**: Choose one of:
  - `foodxchange-openai` (Sweden Central)
  - `foodxchangeopenai` (France Central)
- **Models**: GPT-4 for product description generation

### 3. Azure Storage
- **Purpose**: Store product images
- **Container**: `product-images`
- **Features**: Blob storage for image files

### 4. Azure Cognitive Search (Optional)
- **Purpose**: Advanced product matching and search
- **Index**: Products catalog with AI-enhanced search

## Database Tables

The following tables store AI analysis results:

1. **product_analyses** - AI analysis results from Computer Vision
2. **product_briefs** - Generated product descriptions
3. **product_images** - Image metadata and storage references
4. **ai_insights** - AI-generated market insights

## Environment Variables

Update your `.env` file with the following:

```env
# Computer Vision
AZURE_COMPUTER_VISION_ENDPOINT=https://eastus.api.cognitive.microsoft.com/
AZURE_COMPUTER_VISION_KEY=<your-key>

# OpenAI
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Storage
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
```

## Quick Start

1. Get the keys from Azure Portal for each service
2. Update the `.env` file with your keys
3. Run the application: `python start.py`
4. Access the AI features at: http://localhost:8001/product-analysis