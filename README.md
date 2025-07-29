# FoodXchange - AI-Powered B2B Food Sourcing Platform

A streamlined, AI-powered B2B food sourcing platform that connects buyers with suppliers through intelligent product analysis and matching.

## 🚀 Features

### AI Product Analysis
- **Image Upload & Analysis** - Upload product images for instant AI analysis
- **Text Search** - Search products by name or description
- **Product Brief Generation** - Get detailed specifications and requirements
- **Packaging Suggestions** - AI-recommended packaging options (100g, 250g, 500g, 1kg, etc.)
- **Supplier Matching** - Find similar products from verified suppliers

### Core Platform
- **Supplier Management** - Browse and manage supplier network
- **RFQ System** - Create and manage Requests for Quotes
- **Quote Comparison** - Compare supplier quotes and pricing
- **Order Management** - Track orders and deliveries
- **User Authentication** - Secure login and registration

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Bootstrap 5 + Custom CSS
- **Database**: PostgreSQL
- **AI Services**: Azure Computer Vision + OpenAI
- **Deployment**: Azure App Service

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Azure account (for AI services)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FoodXchange
   ```

2. **Install dependencies**
   ```bash
   pip install -r foodxchange/requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@localhost/foodxchange
   
   # Azure AI Services (optional for demo)
   AZURE_VISION_ENDPOINT=https://your-vision-service.cognitiveservices.azure.com/
   AZURE_VISION_KEY=your_vision_key
   AZURE_OPENAI_API_KEY=your_openai_key
   AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   
   # Security
   SECRET_KEY=your-secret-key-here
   ```

4. **Set up database**
   ```bash
   # Run the database setup script
   python database/setup_database.py
   ```

5. **Start the application**
   ```bash
   cd foodxchange
   python main.py
   ```

6. **Access the application**
   - Main App: http://localhost:8000
   - AI Analysis: http://localhost:8000/product-analysis
   - API Docs: http://localhost:8000/docs

## 🎯 Quick Start

### Try AI Product Analysis

1. **Visit the AI Analysis page**: http://localhost:8000/product-analysis

2. **Upload an image** or **search by text**:
   - Drag & drop a product image
   - Or search for products like "Organic dried cranberries"

3. **View AI results**:
   - Product identification and categorization
   - Detailed specifications and requirements
   - Packaging suggestions (100g, 250g, 500g, 1kg)
   - Similar products from suppliers

### Demo Mode

The system includes a **demo mode** that simulates AI analysis without requiring Azure services. Perfect for testing and demonstrations!

## 📁 Project Structure

```
FoodXchange/
├── foodxchange/
│   ├── main.py                 # Main FastAPI application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection
│   ├── routes/                # API route handlers
│   │   ├── product_analysis_routes.py  # AI analysis endpoints
│   │   ├── supplier_routes.py          # Supplier management
│   │   ├── product_routes.py           # Product catalog
│   │   └── ...                # Other route modules
│   ├── services/              # Business logic
│   │   ├── product_analysis_service.py # AI analysis service
│   │   └── ...                # Other services
│   ├── models/                # Database models
│   └── static/                # Static assets
│       ├── brand/             # Branding and logos
│       └── bootstrap/         # Bootstrap framework
├── database/
│   ├── sourcing_schema.sql    # Database schema
│   └── setup_database.py      # Database setup script
└── README.md
```

## 🔧 Configuration

### Azure AI Services Setup

1. **Create Azure resources**:
   ```bash
   # Create resource group
   az group create --name foodxchange-ai-rg --location eastus
   
   # Create Computer Vision service
   az cognitiveservices account create \
     --name foodxchange-vision \
     --resource-group foodxchange-ai-rg \
     --location eastus \
     --kind ComputerVision \
     --sku S1
   
   # Create OpenAI service
   az cognitiveservices account create \
     --name foodxchange-openai \
     --resource-group foodxchange-ai-rg \
     --location eastus \
     --kind OpenAI \
     --sku S0
   ```

2. **Get service keys** and update your `.env` file

### Database Setup

The system uses a lean, focused schema optimized for food sourcing:

- **Users** - User accounts and authentication
- **Suppliers** - Supplier information and ratings
- **Products** - Product catalog and specifications
- **RFQs** - Request for Quotes
- **Quotes** - Supplier quotes and pricing
- **Orders** - Purchase orders
- **Product Analyses** - AI analysis results
- **Product Briefs** - Generated product briefs

## 🎨 UI/UX Features

- **Modern Bootstrap Design** - Clean, professional interface
- **Responsive Layout** - Works on all devices
- **Drag & Drop Upload** - Easy image upload
- **Real-time Analysis** - Live AI processing feedback
- **Interactive Results** - Rich, structured analysis display

## 🚀 Deployment

### Local Development
```bash
cd foodxchange
python main.py
```

### Production Deployment
The application is designed for Azure App Service deployment with PostgreSQL database.

## 📊 API Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the code comments for implementation details
3. Contact the development team

## 📄 License

This project is licensed under the MIT License.

---

**FoodXchange** - Streamlined AI-Powered B2B Food Sourcing