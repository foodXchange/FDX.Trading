# 🍽️ FoodXchange - B2B Food Supply Chain Platform

A comprehensive B2B platform connecting food suppliers with buyers (restaurants, hotels, caterers) through intelligent RFQ management, AI-powered email processing, and advanced analytics.

## 🌟 Features

### Core Features
- **Smart RFQ Management**: Create, manage, and track Requests for Quotes
- **AI-Powered Email Processing**: Automatically extract RFQ information from emails
- **Supplier Management**: Comprehensive supplier verification and rating system
- **Quote Comparison**: Compare and analyze multiple quotes side-by-side
- **Analytics Dashboard**: Real-time insights and performance metrics
- **Agent Management**: Dedicated agent dashboard for supplier representatives
- **Operator Dashboard**: Unified control center for system administration

### User Roles
- **Admin**: Full system access and management
- **Buyer**: Create RFQs, compare quotes, manage suppliers
- **Supplier**: View RFQs, submit quotes, manage profile
- **Agent**: Represent suppliers, manage proposals and samples
- **Operator**: System-wide monitoring and control

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Node.js (for frontend assets)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/foodxchange.git
cd foodxchange
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up database**
```bash
python setup_database.py
```

5. **Start the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
foodxchange/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   ├── routes/              # Route handlers
│   │   └── agent_routes.py  # Agent-specific routes
│   ├── agents/              # Agent management
│   ├── repositories/        # Data access layer
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # Static assets (CSS, JS, images)
├── migrations/              # Database migrations
├── docs/                    # Documentation
├── data/                    # Data files and exports
├── uploads/                 # File uploads
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies
├── alembic.ini             # Alembic configuration
├── setup_database.py       # Database setup script
├── deploy.bat              # Windows deployment script
├── azure-deploy.ps1        # Azure deployment script
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/foodxchange_db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# OpenAI (for AI features)
OPENAI_API_KEY=your-openai-api-key
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Application Routes

#### Core Pages
- `GET /` - Landing page
- `GET /dashboard` - Main dashboard
- `GET /health` - Health check endpoint

#### Supplier Management
- `GET /suppliers` - List all suppliers
- `GET /suppliers/add` - Add new supplier form
- `GET /suppliers/{id}` - View supplier details
- `GET /suppliers/{id}/edit` - Edit supplier form

#### RFQ Management
- `GET /rfq/new` - Create new RFQ form
- `POST /rfq/new` - Submit new RFQ

#### Analytics & Intelligence
- `GET /analytics` - Analytics dashboard
- `GET /emails` - Email intelligence
- `GET /quotes/comparison` - Quote comparison tool

#### Agent Features
- `GET /agent-dashboard` - Agent dashboard
- `GET /projects` - Project management

#### Operator Features
- `GET /operator` - Operator dashboard

## 🧪 Testing

Run the application:

```bash
uvicorn app.main:app --reload
```

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

## 🚢 Deployment

### Azure App Service

The application includes Azure deployment scripts:

1. **Windows Deployment**
```bash
deploy.bat
```

2. **PowerShell Deployment**
```powershell
.\azure-deploy.ps1
```

3. **Manual Deployment**
```bash
python make_deploy_zip.py
# Upload app.zip to Azure App Service
```

### Production Considerations

1. **Database**: Use Azure Database for PostgreSQL
2. **Environment Variables**: Configure in Azure App Service settings
3. **Static Files**: Ensure proper static file serving
4. **Logging**: Configure application logging
5. **Monitoring**: Use Azure Monitor for performance tracking

## 📊 Data Management

The application includes comprehensive data management:

### Data Files
- **Suppliers**: CSV exports and management
- **Products**: Product catalog and categories
- **Orders**: Order tracking and management
- **Analytics**: Performance metrics and reports
- **Procedures**: Business process documentation

### Database Setup
```bash
python setup_database.py
```

This script will:
- Create database tables
- Import initial data
- Set up indexes and constraints
- Configure sample data

## 🎨 Frontend

The application uses:
- **Jinja2 Templates**: Server-side rendering
- **Static Assets**: CSS, JavaScript, and images
- **Responsive Design**: Mobile-friendly interface
- **Modern UI**: Clean, professional interface

## 🔐 Security

- **CORS Configuration**: Proper cross-origin settings
- **Input Validation**: Form validation and sanitization
- **Database Security**: Parameterized queries
- **Environment Variables**: Secure configuration management

## 📈 Analytics & Reporting

### Key Metrics
- Total spend tracking
- Cost savings analysis
- Supplier engagement rates
- RFQ performance metrics
- Quote comparison analytics

### Reports Available
- Supplier performance reports
- Order analytics
- Cost analysis
- Commission tracking
- Shipping and logistics reports

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- SQLAlchemy for the powerful ORM
- Jinja2 for templating
- All contributors and testers

## 📞 Support

For support, email support@foodxchange.com or create an issue in the repository.

---

**Built with ❤️ by the FoodXchange Team** 