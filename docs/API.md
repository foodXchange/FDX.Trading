# FoodXchange API Documentation

## Overview

The FoodXchange API provides a comprehensive REST API for managing B2B food supply chain operations. The API is built with FastAPI and provides automatic interactive documentation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

The API uses JWT-based authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Health Check

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "ok"
}
```

### Core Pages

#### GET /
Landing page with application overview.

#### GET /dashboard
Main dashboard with key metrics and navigation.

**Response:** HTML page with dashboard interface

### Supplier Management

#### GET /suppliers
List all suppliers with filtering and pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `status` (string): Filter by status (active, pending, inactive)
- `country` (string): Filter by country
- `category` (string): Filter by product category

**Response:**
```json
{
  "suppliers": [
    {
      "id": 1,
      "name": "Mediterranean Delights",
      "location": "Greece",
      "products": ["Olive Oil", "Feta Cheese"],
      "status": "active",
      "rating": 4.8,
      "verified": true
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

#### GET /suppliers/add
Display form for adding a new supplier.

#### GET /suppliers/{supplier_id}
Get detailed information about a specific supplier.

**Path Parameters:**
- `supplier_id` (int): Supplier ID

**Response:**
```json
{
  "id": 1,
  "name": "Mediterranean Delights",
  "location": "Greece",
  "products": ["Olive Oil", "Feta Cheese"],
  "status": "active",
  "rating": 4.8,
  "verified": true,
  "contact_info": {
    "email": "contact@mediterranean.com",
    "phone": "+30 123 456 789",
    "address": "123 Olive Street, Athens"
  },
  "certifications": ["ISO 9001", "Organic Certified"],
  "performance_metrics": {
    "response_rate": 95.5,
    "delivery_time": 7.2,
    "quality_score": 4.9
  }
}
```

#### GET /suppliers/{supplier_id}/edit
Display form for editing supplier information.

### RFQ Management

#### GET /rfq/new
Display form for creating a new RFQ.

#### POST /rfq/new
Create a new Request for Quote.

**Request Body:**
```json
{
  "product": "Olive Oil",
  "quantity": 1000,
  "deadline": "2024-08-15",
  "notes": "Extra virgin olive oil, premium quality required"
}
```

**Response:**
```json
{
  "id": 123,
  "status": "created",
  "message": "RFQ created successfully"
}
```

### Analytics

#### GET /analytics
Analytics dashboard with key performance indicators.

**Response:**
```json
{
  "kpis": {
    "total_spend": 100000,
    "cost_savings": 15000,
    "suppliers_engaged": 12,
    "rfqs_sent": 34
  },
  "charts": {
    "monthly_spend": [...],
    "supplier_performance": [...],
    "category_distribution": [...]
  }
}
```

### Email Intelligence

#### GET /emails
Email intelligence dashboard with AI-processed insights.

**Response:**
```json
{
  "emails": [
    {
      "id": 1,
      "sender": "supplier1@example.com",
      "subject": "Quote for Olive Oil",
      "date": "2024-06-01",
      "insight": "Potential cost savings identified.",
      "confidence": 0.95,
      "extracted_data": {
        "product": "Olive Oil",
        "quantity": 500,
        "price": 1200
      }
    }
  ]
}
```

### Quote Comparison

#### GET /quotes/comparison
Quote comparison tool for analyzing multiple quotes.

**Query Parameters:**
- `rfq_id` (int): RFQ ID to compare quotes for

**Response:**
```json
{
  "rfq": {
    "id": 123,
    "title": "Olive Oil Supply",
    "deadline": "2024-08-15"
  },
  "quotes": [
    {
      "supplier": "Mediterranean Delights",
      "product": "Olive Oil",
      "price": 1200,
      "lead_time": 7,
      "notes": "Includes shipping.",
      "score": 85.5
    },
    {
      "supplier": "Italian Fine Foods",
      "product": "Olive Oil",
      "price": 1250,
      "lead_time": 10,
      "notes": "Faster delivery available.",
      "score": 82.3
    }
  ],
  "recommendations": [
    {
      "type": "best_overall",
      "quote_id": 1,
      "reason": "Highest overall score (85.5)"
    }
  ]
}
```

### Agent Features

#### GET /agent-dashboard
Agent dashboard for supplier representatives.

#### GET /projects
Project management interface.

**Response:**
```json
{
  "projects": [
    {
      "name": "Summer Sourcing 2024",
      "status": "Active",
      "start_date": "2024-05-01",
      "end_date": "2024-08-31",
      "progress": 65
    }
  ]
}
```

### Operator Features

#### GET /operator
Operator dashboard for system administration.

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with the following parameters:

- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)

Response includes pagination metadata:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Sorting

Many endpoints support filtering and sorting:

### Filtering
Use query parameters to filter results:
```
GET /suppliers?status=active&country=Greece&category=Olive Oil
```

### Sorting
Use `sort` parameter with field and direction:
```
GET /suppliers?sort=name:asc
GET /suppliers?sort=rating:desc
```

## Webhooks

The API supports webhooks for real-time notifications:

### Webhook Events
- `rfq.created` - New RFQ created
- `quote.submitted` - New quote submitted
- `supplier.verified` - Supplier verification completed
- `order.created` - New order created

### Webhook Configuration
```json
{
  "url": "https://your-domain.com/webhooks",
  "events": ["rfq.created", "quote.submitted"],
  "secret": "your-webhook-secret"
}
```

## SDKs and Libraries

### Python
```python
import requests

base_url = "https://api.foodxchange.com"
headers = {"Authorization": "Bearer your-token"}

# Get suppliers
response = requests.get(f"{base_url}/suppliers", headers=headers)
suppliers = response.json()
```

### JavaScript
```javascript
const baseUrl = 'https://api.foodxchange.com';
const headers = { 'Authorization': 'Bearer your-token' };

// Get suppliers
const response = await fetch(`${baseUrl}/suppliers`, { headers });
const suppliers = await response.json();
```

## Support

For API support:
- Email: api-support@foodxchange.com
- Documentation: https://docs.foodxchange.com
- Status page: https://status.foodxchange.com 