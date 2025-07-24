# API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints require Bearer token:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication
```
POST /token
Body: { username, password }
Response: { access_token, token_type }
```

### Suppliers
```
GET /suppliers
Query: ?limit=100&skip=0&search=olive
Response: Array of suppliers

POST /suppliers
Body: { name, email, location, products }
Response: Created supplier

PUT /suppliers/{id}
Body: { fields to update }
Response: Updated supplier
```

### Email Analysis
```
POST /analyze-email
Body: { email_content, supplier_id? }
Response: { 
  classification, 
  confidence, 
  suggested_action 
}
```

### Analytics
```
GET /analytics/dashboard
Response: Dashboard statistics

GET /predictions/{product}
Response: Price predictions
```

### Campaigns
```
POST /campaigns
Body: { name, suppliers, template }
Response: Campaign details

GET /campaigns/{id}/status
Response: Campaign metrics
```

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error 