# Azure OpenAI Setup Guide for FoodXchange

## 🚀 Quick Setup Steps

### 1. Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"+ Create a resource"**
3. Search for **"Azure OpenAI"**
4. Click **Create**

### 2. Configure the Resource

```
Resource Group: foodxchange-rg
Name: foodxchange-openai
Region: France Central (or same as your other resources)
Pricing Tier: Standard S0
```

### 3. Deploy a Model

After creation:
1. Go to your OpenAI resource
2. Click **"Model deployments"** → **"Manage Deployments"**
3. Click **"+ Create new deployment"**

Recommended models:
- **GPT-4**: Best for complex analysis (email parsing, insights)
- **GPT-3.5-Turbo**: Faster and cheaper for simple tasks

```
Deployment name: gpt-4
Model: gpt-4 (or gpt-35-turbo)
Model version: Latest
Capacity: 10K TPM (tokens per minute)
```

### 4. Get Your Credentials

1. Go to **"Keys and Endpoint"**
2. Copy:
   - **Endpoint**: `https://foodxchange-openai.openai.azure.com/`
   - **Key**: (either KEY 1 or KEY 2)

### 5. Update Your .env File

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://foodxchange-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

## 📦 Install Required Package

```bash
pip install openai
```

## 🧪 Test the Integration

Create `test_openai.py`:

```python
import os
from app.services.openai_service import openai_service

# Test email parsing
test_email = """
Subject: Urgent RFQ - Premium Olive Oil

Hi,

We need a quote for:
- 500 liters of Extra Virgin Olive Oil
- Delivery by end of month
- Organic certification required

Please send your best price.

Thanks,
John from Restaurant Chain
"""

async def test():
    result = await openai_service.parse_email_for_rfq(test_email)
    print("Parsed RFQ:", result)

# Run test
import asyncio
asyncio.run(test())
```

## 💡 Features Enabled by OpenAI

### 1. **Email Intelligence**
- Automatically extract RFQs from emails
- Identify quotes and orders
- Parse product requirements

### 2. **Smart Supplier Matching**
- AI-powered supplier recommendations
- Match based on requirements
- Rank by compatibility

### 3. **Quote Analysis**
- Compare quotes intelligently
- Identify best value (not just price)
- Negotiation suggestions

### 4. **Insights Generation**
- Purchasing pattern analysis
- Cost-saving opportunities
- Market trend detection

## 💰 Cost Management

### Estimated Costs:
- **Email Parsing**: ~$0.002 per email
- **Supplier Matching**: ~$0.005 per search
- **Quote Analysis**: ~$0.003 per comparison

### Cost Controls:
1. Set spending limits in Azure
2. Use GPT-3.5-Turbo for simple tasks
3. Cache results when possible
4. Batch similar requests

## 🔒 Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Rotate keys regularly** - Azure supports 2 keys
3. **Set up monitoring** - Track usage and anomalies
4. **Use managed identity** - For App Service deployment

## 🎯 Next Steps

1. **Test email parsing** with real emails
2. **Fine-tune prompts** for your industry
3. **Add more AI features**:
   - Contract analysis
   - Price trend prediction
   - Supplier risk assessment

## 📚 Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)