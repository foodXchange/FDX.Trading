# Azure Services Testing Guide

## Overview
This guide explains how to use the Azure Testing Dashboard to test real Azure services with cost monitoring and free tier limits.

## Features

### 1. Real Azure Service Testing
- **GPT-4 Vision**: Analyze product images and extract information
- **Document Intelligence**: Extract data from PDFs and documents
- **Translator**: Translate multilingual CSV files
- **Computer Vision**: Analyze images for product information

### 2. Cost Monitoring & Alerts
- Real-time cost tracking
- Budget alerts and notifications
- Usage limit warnings
- Cost anomaly detection

### 3. Usage Analytics
- Detailed usage patterns analysis
- Cost forecasting
- Optimization recommendations
- Service performance metrics

## Getting Started

### 1. Configure Azure Services
Ensure your `.env` file contains all required Azure credentials:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_VISION_DEPLOYMENT=gpt-4o

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-docint.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key

# Azure Translator
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
AZURE_TRANSLATOR_KEY=your-key
AZURE_TRANSLATOR_REGION=eastus

# Azure Computer Vision
AZURE_VISION_ENDPOINT=https://your-vision.cognitiveservices.azure.com/
AZURE_VISION_KEY=your-key
```

### 2. Generate Test Data
Run the test data generator to create sample files:

```bash
cd test_data
python generate_test_data.py
```

This creates:
- `suppliers_hebrew.csv` - Hebrew supplier data
- `products_multilingual.csv` - Multilingual product catalog
- `hebrew_product_label.jpg` - Sample Hebrew product label
- `catalog_page.jpg` - Product catalog page
- `invoice_sample.csv` - Sample invoice data

### 3. Access the Testing Dashboard
Navigate to: `http://localhost:8003/azure-test/`

## Testing Scenarios

### 1. Product Image Analysis
**Purpose**: Test GPT-4 Vision for extracting product information from images

**Steps**:
1. Upload a product image (JPEG/PNG)
2. View extracted information (name, brand, ingredients, etc.)
3. Check processing time and cost

**Free Tier Limits**:
- 10,000 tokens per minute
- 3 requests per minute

### 2. CSV Translation
**Purpose**: Test multilingual data translation

**Steps**:
1. Upload a CSV file with non-English text
2. Select source and target languages
3. Preview translated data
4. Monitor character usage

**Free Tier Limits**:
- 2 million characters per month (free)

### 3. Document Analysis
**Purpose**: Extract structured data from documents

**Steps**:
1. Upload a PDF or image document
2. View extracted tables, key-value pairs, and text
3. Check page processing count

**Free Tier Limits**:
- 500 pages per month

## Cost Monitoring

### Setting Up Alerts

1. Go to the Alerts section in the dashboard
2. Configure alerts for:
   - Daily budget ($5 default)
   - Monthly budget ($50 default)
   - Service limit warnings (80% threshold)
   - Cost anomalies (3x normal usage)

### Alert Types

- **Cost Threshold**: Triggered when spending exceeds limit
- **Limit Warning**: Triggered when approaching service limits
- **Budget Exceeded**: Triggered when budget is exceeded
- **Anomaly Detected**: Triggered on unusual usage patterns

### Notification Options

- Email notifications (configure SMTP in .env)
- Webhook notifications for integration

## Usage Analytics

### Available Metrics

1. **Hourly Patterns**: Peak usage hours identification
2. **Daily Trends**: Cost and usage trends over time
3. **Service Performance**: Success rates and processing times
4. **Error Analysis**: Common error patterns and causes

### Cost Optimization

The system provides:
- Caching recommendations for repeated operations
- Batching suggestions for multiple operations
- Service-specific optimization tips

## API Endpoints

### Testing Endpoints
- `POST /azure-test/api/test/product-image` - Test image analysis
- `POST /azure-test/api/test/csv-translation` - Test translation
- `POST /azure-test/api/test/document-analysis` - Test document OCR

### Monitoring Endpoints
- `GET /azure-test/api/status` - Service status and limits
- `GET /azure-test/api/usage/summary` - Usage summary
- `GET /azure-test/api/usage/history` - Detailed history
- `GET /azure-test/api/usage/export` - Export data as CSV

### Analytics Endpoints
- `GET /azure-test/api/analytics` - Usage patterns analysis
- `GET /azure-test/api/cost-forecast` - Cost projections
- `GET /azure-test/api/optimization-opportunities` - Optimization tips

### Alert Management
- `GET /azure-test/api/alerts` - List all alerts
- `POST /azure-test/api/alerts` - Create new alert
- `PUT /azure-test/api/alerts/{id}` - Update alert
- `DELETE /azure-test/api/alerts/{id}` - Delete alert

## Best Practices

### 1. Stay Within Free Tier Limits
- Monitor usage percentages on dashboard
- Set up alerts before reaching limits
- Use caching for repeated operations

### 2. Optimize API Calls
- Batch multiple operations when possible
- Use appropriate file sizes
- Implement client-side validation

### 3. Cost Management
- Review daily usage patterns
- Act on optimization recommendations
- Set realistic budget alerts

### 4. Error Handling
- Monitor error rates
- Review error patterns in analytics
- Implement retry logic for transient errors

## Troubleshooting

### Common Issues

1. **"Service not configured" errors**
   - Check .env file for missing credentials
   - Verify Azure service endpoints are correct

2. **Rate limit errors**
   - Check current usage on dashboard
   - Wait for limit reset (usually 1 minute for rate limits)

3. **High costs**
   - Review optimization opportunities
   - Enable caching for repeated operations
   - Consider batching requests

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Cost Estimates

| Operation | Estimated Cost | Notes |
|-----------|---------------|-------|
| Product Image Analysis | $0.03 per image | GPT-4 Vision |
| CSV Translation (1000 rows) | $0.02 | Based on average row length |
| Document Analysis | $0.0015 per page | Document Intelligence |
| Catalog OCR | $0.05 per page | Multiple products |

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **File Uploads**: Temporary files are automatically cleaned up
3. **Data Privacy**: Test data is not stored permanently
4. **Access Control**: Implement authentication for production use

## Future Enhancements

1. **Batch Processing**: Queue system for large batches
2. **Scheduled Tests**: Automated testing schedules
3. **Custom Models**: Fine-tuned models for specific use cases
4. **Advanced Analytics**: ML-based cost predictions

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Azure service documentation
3. Contact system administrator for credential issues