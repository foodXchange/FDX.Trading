# Configuration Guide

## Environment Variables

### Required
```env
# Security
SECRET_KEY=<random-string-min-32-chars>

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_DEPLOYMENT_NAME=gpt-4

# Database
COSMOS_ENDPOINT=https://<account>.documents.azure.com:443/
COSMOS_KEY=<your-key>
COSMOS_DATABASE=foodxchange
```

### Optional
```env
# Email (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<email>
SMTP_PASSWORD=<app-password>

# Features
ENABLE_AI_PREDICTIONS=true
ENABLE_EMAIL_AUTOMATION=true
MAX_SUPPLIERS=50000
```

## Email Templates
Located in `backend/templates/`:
- welcome_supplier.html
- initial_inquiry.html
- follow_up.html
- price_negotiation.html

## AI Settings
Edit `backend/ai_config.py`:
```python
AI_CONFIG = {
    "temperature": 0.3,
    "max_tokens": 500,
    "response_timeout": 30
}
```

## Database Schema
Collections:
- suppliers
- emails
- campaigns
- analytics
- workflows 