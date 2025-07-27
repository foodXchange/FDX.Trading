# 🚀 Bootstrap Quick Start Guide - Food Xchange

## 🎯 Overview
This guide will help you quickly deploy and test the Bootstrap implementation for your Food Xchange platform.

## 📋 Prerequisites
- Python 3.8+ installed
- FastAPI and Uvicorn installed
- PowerShell (for Windows) or Terminal (for Mac/Linux)

## 🚀 Quick Deployment

### Step 1: Run the Deployment Script
```powershell
.\deploy-bootstrap.ps1
```

This script will:
- ✅ Check all Bootstrap files are present
- ✅ Verify FastAPI dependencies
- ✅ Create test and startup scripts
- ✅ Prepare everything for deployment

### Step 2: Start the Server
```powershell
.\start-bootstrap.ps1
```

Or manually:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Access Your Bootstrap Screens

Open your browser and visit:

| Screen | URL | Description |
|--------|-----|-------------|
| **RFQ Form** | `http://localhost:8000/bootstrap/rfq` | Create new RFQs |
| **Order Management** | `http://localhost:8000/bootstrap/orders` | Manage orders |
| **Analytics** | `http://localhost:8000/bootstrap/analytics` | View business metrics |
| **Help & Support** | `http://localhost:8000/bootstrap/help` | Get help and support |

## 🧪 Testing the Deployment

### Automated Test
```bash
python test_bootstrap_deployment.py
```

### Manual Testing
1. Visit each URL above
2. Test form submissions
3. Check responsive design
4. Verify Food Xchange branding

## 🔧 Working with Bootstrap Screens

### File Locations
```
app/
├── templates/bootstrap/
│   ├── base.html              # Base template with navigation
│   ├── rfq-form.html          # RFQ creation form
│   ├── order-management.html  # Order management interface
│   ├── analytics.html         # Analytics dashboard
│   └── help.html              # Help & support center
├── routes/
│   └── bootstrap_routes.py    # API endpoints
└── static/bootstrap/          # Bootstrap assets
```

### Making Changes
1. **Edit Templates**: Modify files in `app/templates/bootstrap/`
2. **Update Routes**: Edit `app/routes/bootstrap_routes.py`
3. **Add Styles**: Create custom CSS in `app/static/bootstrap/`
4. **Test Changes**: Refresh your browser to see updates

### Customization Examples

#### Adding a New Field to RFQ Form
```html
<!-- In app/templates/bootstrap/rfq-form.html -->
<div class="mb-3">
    <label for="newField" class="form-label">New Field</label>
    <input type="text" class="form-control" id="newField">
</div>
```

#### Adding a New API Endpoint
```python
# In app/routes/bootstrap_routes.py
@router.get("/api/new-endpoint")
async def new_endpoint():
    return {"message": "New endpoint"}
```

## 🎨 Brand Customization

### Colors
The Bootstrap screens use your Food Xchange brand colors:
- **Primary**: #4A90E2 (Teal)
- **Secondary**: #F97316 (Orange)
- **Success**: #10B981 (Green)

### Fonts
- **UI Elements**: Causten
- **Headings**: David Libre
- **Body Text**: Roboto Serif

### Logo
Your Food Xchange logo is displayed in the navigation bar.

## 📱 Responsive Design

All Bootstrap screens are mobile-responsive:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

Test on different screen sizes to ensure proper display.

## 🔌 API Integration

### Available Endpoints
- `POST /bootstrap/api/rfq` - Create RFQ
- `GET /bootstrap/api/orders` - Get orders
- `GET /bootstrap/api/analytics/metrics` - Get analytics
- `POST /bootstrap/api/support/contact` - Submit support ticket

### Testing APIs
Use tools like Postman or curl to test API endpoints:
```bash
curl -X GET http://localhost:8000/bootstrap/api/orders
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Error: No module named 'app.routes.bootstrap_routes'
**Solution**: Make sure you're running from the project root directory.

#### 2. Template Not Found
**Solution**: Check that all Bootstrap template files exist in `app/templates/bootstrap/`.

#### 3. Bootstrap CSS/JS Not Loading
**Solution**: The templates use CDN links, so ensure internet connectivity.

#### 4. Port Already in Use
**Solution**: Change the port in the startup command:
```bash
python -m uvicorn app.main:app --port 8001 --reload
```

### Debug Mode
For detailed error messages, run with debug:
```bash
python -m uvicorn app.main:app --reload --log-level debug
```

## 🚀 Production Deployment

### For Production
1. Remove `--reload` flag
2. Set proper host and port
3. Configure environment variables
4. Set up reverse proxy (nginx/Apache)

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 80
```

### Environment Variables
```bash
export DATABASE_URL="your_database_url"
export SECRET_KEY="your_secret_key"
export ENVIRONMENT="production"
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the error logs
3. Test individual components
4. Verify all dependencies are installed

## 🎉 Success!

Once deployed, you'll have:
- ✅ Fully functional Bootstrap screens
- ✅ Food Xchange branding
- ✅ Responsive design
- ✅ API integration
- ✅ Form validation
- ✅ Interactive components

Your Food Xchange platform is now ready with modern, professional Bootstrap interfaces! 