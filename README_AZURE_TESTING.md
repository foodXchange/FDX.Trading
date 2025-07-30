# Azure API Connection Testing Suite

This comprehensive testing suite helps you verify all your Azure service connections for the FoodXchange project.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r azure_requirements.txt
```

### 2. Set Up Environment Variables

**Windows:**
```cmd
setup_env.bat
```

**Linux/Mac:**
```bash
chmod +x setup_env.sh
./setup_env.sh
```

### 3. Run Complete Test Suite

**Windows:**
```cmd
run_all_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

## 📋 What Gets Tested

### Azure Services Covered:
- **Document Intelligence** - OCR and form processing
- **Computer Vision** - Image analysis and object detection
- **Translator** - Text translation services
- **Azure OpenAI** - GPT models and chat completions
- **Azure Storage** - Blob storage connectivity

### Test Types:
1. **Endpoint Validation** - Checks URL and key formats
2. **Quick Health Check** - 30-second connectivity test
3. **Full Connection Test** - Comprehensive API testing with real operations

## 🔧 Individual Scripts

### `validate_endpoints.py`
Validates the format of your Azure endpoints and keys:
```bash
python validate_endpoints.py
```

**Checks:**
- Endpoint URL format (must match Azure patterns)
- Key format (32-character hexadecimal)
- Required environment variables

### `quick_health_check.py`
Fast 30-second health check of all services:
```bash
python quick_health_check.py
```

**Tests:**
- Basic connectivity to each service
- Minimal API calls to verify access
- Quick status summary

### `azure_connection_test.py`
Comprehensive testing with real operations:
```bash
python azure_connection_test.py
```

**Performs:**
- Document text extraction from test image
- Image analysis with object detection
- Hebrew to English translation
- OpenAI chat completion
- Storage container listing

## 📊 Test Results

### Console Output
Real-time progress with emojis and status indicators:
```
🔍 Starting Azure API Connection Tests...
==================================================

📄 Testing Document Intelligence...
   ✅ Connected successfully (2.34s)
   📊 Processed 1 pages
   📝 Extracted 156 characters

👁️ Testing Computer Vision...
   ✅ Connected successfully (1.87s)
   🏷️ Detected 15 tags
```

### JSON Report
Detailed report saved as `azure_connection_test_YYYYMMDD_HHMMSS.json`:
```json
{
  "timestamp": "2024-01-15T10:30:45",
  "summary": {
    "total_services": 5,
    "successful": 5,
    "failed": 0,
    "success_rate": "100.0%"
  },
  "results": {
    "document_intelligence": {
      "status": "✅ SUCCESS",
      "response_time": "2.34s",
      "endpoint": "https://your-resource.cognitiveservices.azure.com",
      "pages_processed": 1,
      "text_extracted": 156
    }
  }
}
```

## 🔑 Environment Variables

Create a `.env` file with your Azure credentials:

```env
# Azure Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com
DOCUMENT_INTELLIGENCE_KEY=your-32-character-key

# Azure Computer Vision
COMPUTER_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com
COMPUTER_VISION_KEY=your-32-character-key

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your-32-character-key

# Azure Translator
TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
TRANSLATOR_KEY=your-32-character-key

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
```

## 🛠️ Troubleshooting

### Common Issues:

**1. Missing Environment Variables**
```
❌ Missing credentials
💡 Run setup_env.sh to configure your Azure credentials
```

**2. Invalid Endpoint Format**
```
❌ Invalid format
💡 Should be: https://your-resource.cognitiveservices.azure.com
```

**3. Authentication Errors**
```
❌ Connection failed: HTTP 401: Unauthorized
💡 Check your API keys in Azure Portal > Keys and Endpoint
```

**4. Network Issues**
```
❌ Connection failed: Connection timeout
💡 Check your internet connection and firewall settings
```

### Getting Azure Credentials:

1. **Go to Azure Portal** → Your Resource
2. **Navigate to** → Keys and Endpoint
3. **Copy** the endpoint URL and key
4. **Use either** Key 1 or Key 2

## 📈 Performance Metrics

The tests measure:
- **Response Time** - How fast each service responds
- **Success Rate** - Percentage of successful connections
- **Token Usage** - OpenAI API consumption
- **Cost Estimates** - Approximate API costs

## 🔄 Integration with FoodXchange

These tests verify the same Azure services used by:
- **Product Analysis** - Computer Vision + Document Intelligence
- **AI Processing** - Azure OpenAI for analysis
- **Translation** - Multi-language support
- **File Storage** - Azure Blob Storage for uploads

## 🚨 Security Notes

- Never commit your `.env` file to version control
- Use Azure Key Vault for production environments
- Rotate API keys regularly
- Monitor API usage and costs

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Azure service is active and billing is set up
3. Ensure you have the correct permissions for each service
4. Review the detailed JSON report for specific error messages 