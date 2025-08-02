# FoodXchange API Reference

## Overview

The FoodXchange API provides comprehensive endpoints for B2B food sourcing operations, AI-powered product analysis, and business relationship management.

**Base URL**: `http://localhost:9000` (development)  
**API Version**: v1  
**Authentication**: JWT Bearer Token in HTTPOnly Cookie

## Authentication

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

email=admin@fdx.trading&password=FDX2030!
```

**Response:**
```http
HTTP/1.1 303 See Other
Location: /dashboard
Set-Cookie: access_token=eyJ...; HttpOnly; Secure; SameSite=Strict
```

### Logout
```http
POST /auth/logout
```

### Registration
```http
POST /auth/signup
Content-Type: application/x-www-form-urlencoded

firstName=John&lastName=Doe&email=john@company.com&password=SecurePass123&confirmPassword=SecurePass123&company=FoodCorp
```

## Core Application Endpoints

### Dashboard
```http
GET /dashboard
Authorization: Required (JWT Cookie)
```

**Response:**
```html
<!-- Dashboard HTML with user context -->
```

### User Profile
```http
GET /profile
Authorization: Required (JWT Cookie)
```

**Response:**
```html
<!-- Profile management interface -->
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "azure_ai": "available"
  }
}
```

## AI-Powered Features

### Product Analysis
```http
GET /product-analysis/
Authorization: Required (JWT Cookie)
```

**Features:**
- Image upload and analysis using GPT-4 Vision
- Product specification extraction
- Nutritional information analysis
- Kosher and dietary compliance detection
- Multi-language support (Hebrew/English)

### AI Data Import
```http
POST /ai-import
Content-Type: multipart/form-data
Authorization: Required (JWT Cookie)

file=@product_data.xlsx
```

**Response:**
```json
{
  "status": "success",
  "processed_items": 150,
  "ai_enhancements": {
    "category_predictions": 145,
    "specification_extractions": 120,
    "compliance_checks": 150
  },
  "import_id": "imp_abc123"
}
```

### Azure Service Testing
```http
GET /azure-testing
Authorization: Required (Admin Role)
```

**Features:**
- Computer Vision API testing
- Document Intelligence validation
- Translation service verification
- Storage service connectivity

## Business Management

### Project Management
```http
GET /projects
Authorization: Required (JWT Cookie)
```

**Features:**
- 5-stage sourcing workflow tracking
- Project status management (INITIATED → IN_PROGRESS → REVIEW → APPROVED/REJECTED)
- Budget and timeline tracking
- Document and sample management

### Supplier Management
```http
GET /suppliers
Authorization: Required (JWT Cookie)
```

**Features:**
- Supplier contact information
- Certification tracking
- Rating and review system
- Payment terms and minimum orders

### Buyer Management
```http
GET /buyers
Authorization: Required (Admin Role)
```

**Features:**
- Customer relationship management
- Industry and company size tracking
- Preferred categories and requirements
- Verification status management

## Static Pages

### Landing Page
```http
GET /
```

### About & Information Pages
```http
GET /about
GET /contact
GET /privacy
GET /terms
GET /security
```

### Support System
```http
GET /support
Authorization: Required (JWT Cookie)
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": "Authentication failed for user",
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes
- `200 OK` - Success
- `303 See Other` - Redirect after form submission
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

### Limits
- **Login Attempts**: 5 per 5 minutes per IP
- **API Requests**: 100 per minute per user
- **File Uploads**: 10 per hour per user
- **AI Analysis**: 20 per hour per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Security

### Authentication
- JWT tokens with 30-minute expiration
- HTTPOnly cookies with SameSite protection
- bcrypt password hashing with salt

### Authorization Roles
- **Admin**: Full system access
- **Operator**: Business operations access
- **User**: Standard user access

### Security Headers
```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

## File Upload

### Supported Formats
- **Images**: JPG, PNG, WEBP (max 10MB)
- **Documents**: PDF, DOCX, XLSX (max 25MB)
- **Data**: CSV, JSON, XML (max 50MB)

### Upload Endpoint
```http
POST /upload
Content-Type: multipart/form-data
Authorization: Required (JWT Cookie)

file=@document.pdf&type=contract
```

## Webhooks

### Event Types
- `user.created` - New user registration
- `project.status_changed` - Project workflow updates
- `analysis.completed` - AI analysis finished
- `supplier.verified` - Supplier verification complete

### Webhook Payload
```json
{
  "event": "project.status_changed",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "project_id": "proj_123",
    "old_status": "IN_PROGRESS",
    "new_status": "REVIEW",
    "user_id": "user_456"
  }
}
```

## SDKs and Libraries

### Python SDK
```python
from foodxchange_sdk import FoodXchangeClient

client = FoodXchangeClient(
    base_url="https://api.foodxchange.com",
    api_key="your_api_key"
)

# Analyze product
result = client.analyze_product(image_path="product.jpg")
print(result.specifications)
```

### JavaScript SDK
```javascript
import FoodXchange from 'foodxchange-js-sdk';

const client = new FoodXchange({
  baseURL: 'https://api.foodxchange.com',
  apiKey: 'your_api_key'
});

// Create project
const project = await client.projects.create({
  title: 'Organic Vegetables Sourcing',
  category: 'vegetables',
  budget: 50000
});
```

## Development

### API Documentation
- **Interactive Docs**: http://localhost:9000/docs (Swagger UI)
- **ReDoc**: http://localhost:9000/redoc
- **OpenAPI Spec**: http://localhost:9000/openapi.json

### Testing
```bash
# Test authentication
curl -X POST http://localhost:9000/auth/login \
  -d "email=admin@fdx.trading&password=FDX2030!"

# Test health endpoint
curl http://localhost:9000/health

# Test with authentication
curl -b "access_token=your_jwt_token" http://localhost:9000/dashboard
```

### Environment Variables
```bash
# API Configuration
API_VERSION=v1
API_TITLE="FoodXchange API"
API_DESCRIPTION="B2B Food Sourcing Platform API"

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REDIS_URL=redis://localhost:6379

# File Upload
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=jpg,png,pdf,docx,xlsx,csv
UPLOAD_DIRECTORY=./uploads
```

## Support

### Error Reporting
Report API issues to: `api-support@foodxchange.com`

### Status Page
Monitor API status: `https://status.foodxchange.com`

### Rate Limit Support
Contact support for rate limit increases for production usage.

---

*This API reference is automatically generated from the FoodXchange OpenAPI specification.*