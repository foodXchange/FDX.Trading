# FoodXchange Sourcing Module Documentation

Welcome to the FoodXchange Sourcing Module documentation. This lean, focused guide covers the essential aspects of the B2B food sourcing platform.

## 🎯 Project Overview

FoodXchange is a streamlined B2B food sourcing platform that connects buyers with suppliers through an intelligent, AI-powered matching system.

## 🚀 Quick Start

### Development Setup
1. **Install Dependencies**
   ```bash
   pip install -r foodxchange/requirements.txt
   ```

2. **Start Development Server**
   ```bash
   cd foodxchange
   python main.py
   ```

3. **Access Application**
   - Main App: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
foodxchange/
├── main.py              # Main FastAPI application
├── routes/              # API route handlers
│   ├── auth_routes.py   # Authentication
│   ├── supplier_routes.py # Supplier management
│   ├── product_routes.py # Product catalog
│   ├── rfq_routes.py    # RFQ management
│   └── quote_routes.py  # Quote management
├── models/              # Database models
│   ├── user.py          # User management
│   ├── supplier.py      # Supplier data
│   ├── product.py       # Product data
│   ├── rfq.py          # RFQ data
│   └── quote.py        # Quote data
├── services/            # Business logic
│   ├── email_service.py # Email functionality
│   └── notification_service.py # Notifications
├── agents/              # AI agents
│   ├── smart_sourcing_agent.py # Smart sourcing
│   └── csv_data_import_agent.py # CSV import
└── static/              # Static assets
    ├── brand/           # Branding assets
    └── bootstrap/       # Bootstrap framework
```

## 🎯 Core Features

### Sourcing Module
- **Supplier Discovery** - Find and manage suppliers
- **Product Catalog** - Browse and search products
- **RFQ Management** - Create and manage Requests for Quotes
- **Quote Comparison** - Compare and evaluate quotes
- **CSV Import** - Bulk import supplier and product data

### User Management
- **Authentication** - Secure user login and registration
- **Role-based Access** - Different permissions for buyers and suppliers
- **Profile Management** - User and company profiles

## 🔧 Technical Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Bootstrap 5** - Frontend framework

### AI & Automation
- **Smart Sourcing Agent** - AI-powered supplier matching
- **CSV Import Agent** - Automated data import
- **Email Service** - Automated communication

## 📊 Database Schema

### Core Tables
- **users** - User accounts and authentication
- **suppliers** - Supplier information and ratings
- **products** - Product catalog and specifications
- **rfqs** - Request for Quotes
- **quotes** - Supplier quotes and pricing
- **orders** - Purchase orders
- **notifications** - System notifications

## 🚀 Deployment

### Local Development
```bash
cd foodxchange
python main.py
```

### Production
The application is designed to be deployed on Azure App Service with PostgreSQL database.

## 📞 Support

For questions or issues:
1. Check the code comments for implementation details
2. Review the API documentation at `/docs`
3. Contact the development team

---

**FoodXchange Sourcing Module** - Streamlined B2B Food Sourcing 