# FoodXchange - AI-Powered B2B Food Sourcing Platform

An advanced AI-powered platform for B2B food product analysis and sourcing. The system uses Azure Computer Vision and OpenAI to analyze product images, extract detailed information, generate professional documents, and provide intelligent sourcing recommendations.

## 🚀 Key Features

### AI Product Analysis
- **🤖 Advanced Image Analysis** - Uses Azure Computer Vision to analyze product images
- **🌐 Multi-Language Support** - Automatically detects and reads Hebrew, English, and other languages
- **🧠 Machine Learning** - System learns from user corrections to improve accuracy
- **✏️ Real-Time Field Editing** - Click any field to edit - AI learns from your corrections
- **📸 Multi-Image Analysis** - Upload multiple images for comprehensive analysis
- **🔍 Smart Recommendations** - Suggests related products and sourcing options

### Product Analysis Capabilities
- **Product Name & Brand Detection** - Accurately identifies products and brands
- **Company Identification** - Detects producing company information
- **Packaging Analysis** - Identifies packaging type and weight
- **Appearance Description** - Detailed product appearance analysis
- **Kosher Certification** - Detects kosher symbols and Hebrew text
- **Related Products** - Finds products from the same family
- **Sourcing Options** - Provides supplier recommendations

### Document Generation
- **📄 Professional Product Briefs** - Generate DOCX, PDF, or HTML documents
- **✏️ In-Browser Editing** - Edit product details before finalizing
- **📦 Multi-Product Briefs** - Combine multiple products in one document
- **📧 Email Integration** - Send briefs directly to suppliers with Azure Email

### Business Management
- **👥 Buyer Profiles** - Manage buyer information and preferences
- **📊 Project Tracking** - Save and organize product analyses
- **📥 Export Capabilities** - Export data in CSV format
- **🔍 Search & Filter** - Quickly find buyers and projects

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.8+)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Database**: SQLAlchemy with SQLite (local)
- **AI Services**: 
  - Azure OpenAI (GPT-3.5-Turbo)
  - Azure Computer Vision (OCR & Image Analysis)
  - Azure Communication Services (Email)
- **Document Generation**: python-docx, ReportLab
- **Current Port**: 8003

## 📦 Installation

### Prerequisites
- Python 3.8+
- Azure OpenAI API Key
- Azure Computer Vision API Key

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
   # Azure Computer Vision
   AZURE_VISION_ENDPOINT=https://your-region.api.cognitive.microsoft.com/
   AZURE_VISION_KEY=your-vision-key
   
   # Azure OpenAI
   AZURE_OPENAI_API_KEY=your-openai-key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
   
   # Azure Communication Services (optional)
   AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING=your-connection-string
   AZURE_EMAIL_SENDER_ADDRESS=DoNotReply@your-domain.azurecomm.net
   
   # Database
   DATABASE_URL=sqlite:///./foodxchange.db
   ```

4. **Start the application**
   ```bash
   # Windows
   run_server.bat
   
   # Or directly with Python
   python run_server.py
   ```

5. **Access the application**
   - Main App: http://localhost:8003
   - AI Analysis: http://localhost:8003/product-analysis/
   - Dashboard: http://localhost:8003/dashboard
   - API Docs: http://localhost:8003/docs

## 🎯 Quick Start

### Using AI Product Analysis

1. **Visit the AI Analysis page**: http://localhost:8003/product-analysis/

2. **Choose analysis method**:
   - **Upload Files**: Drag & drop or select multiple product images
   - **Image URLs**: Paste direct links to product images

3. **Enhance accuracy** (optional):
   - Add product description for context
   - Select product category

4. **View AI results**:
   - Comprehensive product analysis
   - All fields are editable - click to modify
   - System learns from your corrections

5. **Generate Documents**:
   - Click "Generate Product Brief" to preview
   - Edit any field inline before finalizing
   - Download as DOCX, PDF, or HTML
   - Email directly to suppliers

### Multi-Product Brief Generation

1. **Enable Multi-Product Mode** in the document section
2. **Analyze multiple products** individually
3. **Add each to your selection** using the "Add to Multi-Product List" button
4. **Generate combined brief** with all selected products

### Machine Learning Features

The system includes advanced ML capabilities:
- Learns from every field correction
- Improves accuracy for similar products
- Stores feedback for continuous improvement
- Applies learned patterns to future analyses

## 📁 Project Structure

```
FoodXchange/
├── foodxchange/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection (SQLite)
│   ├── routes/                 # API endpoints
│   │   ├── product_analysis_routes.py  # AI analysis endpoints
│   │   └── buyers_routes.py            # Buyer management
│   ├── services/               # Business logic
│   │   ├── product_analysis_service.py # AI analysis service
│   │   ├── ml_improvement_service.py   # Machine learning service
│   │   ├── openai_service.py           # OpenAI integration
│   │   ├── document_service.py         # Document generation
│   │   └── email_service.py            # Email integration
│   ├── models/                 # Database models
│   │   ├── feedback.py         # ML feedback models
│   │   └── user.py             # User model
│   ├── static/                 # Frontend assets
│   │   ├── brand/              # Logos and fonts
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript files
│   │   └── bootstrap/          # Bootstrap files
│   └── templates/              # HTML templates
│       ├── base.html           # Base template
│       ├── components/         # Reusable components
│       └── pages/              # Page templates
├── run_server.py               # Server startup script
├── run_server.bat              # Windows batch file
├── .env                        # Configuration (create this)
├── AZURE_EMAIL_SETUP.md        # Email setup guide
└── README.md                   # This file
```

## 🔧 Current Status

✅ **Working Features**:
- AI product analysis with Azure Computer Vision & OpenAI
- Hebrew language support with OCR
- Machine learning from user corrections
- Multi-image analysis support
- Real-time field editing
- Document generation (DOCX, PDF, HTML)
- Email integration with Azure
- Multi-product brief generation
- Buyer management system
- Project saving and tracking
- Export capabilities (CSV)
- Template system (Jinja2)
- Dashboard and landing pages
- Product description input for enhanced accuracy

⚙️ **Configuration**:
- Server runs on port 8003
- SQLite database (local)
- No external database required
- All AI services use real Azure endpoints

## 🎨 UI/UX Features

- **Modern Bootstrap Design** - Clean, professional interface
- **Responsive Layout** - Works on desktop and mobile
- **Drag & Drop Upload** - Easy multi-image upload
- **Tab Interface** - Switch between upload and URL input
- **Real-time Feedback** - Live saving indicators
- **Interactive Editing** - Click any field to edit
- **Visual Indicators** - Confidence scores and ML feedback

## 📊 API Documentation

- **Interactive API Docs**: http://localhost:8003/docs
- **Main Endpoints**:
  - `POST /product-analysis/analyze-image` - Single image analysis
  - `POST /product-analysis/analyze-multiple-images` - Multi-image analysis
  - `POST /product-analysis/analyze-image-url` - URL analysis
  - `POST /product-analysis/save-field-edit` - Save ML corrections
  - `POST /product-analysis/submit-feedback` - Submit feedback
  - `POST /product-analysis/generate-brief-preview` - Generate document preview
  - `POST /product-analysis/download-brief/{format}` - Download document
  - `POST /product-analysis/email-brief` - Email product brief
  - `GET /buyers/list` - List all buyers
  - `POST /buyers/add` - Add new buyer

## 🚀 Deployment Notes

### Local Development
- Uses SQLite database (foodxchange.db)
- Uploads stored in local `uploads/` directory
- All templates use custom `url_for` function
- Static files served from `foodxchange/static/`

### Environment Variables Required
```env
# Required
AZURE_VISION_ENDPOINT=<required>
AZURE_VISION_KEY=<required>
AZURE_OPENAI_API_KEY=<required>
AZURE_OPENAI_ENDPOINT=<required>
AZURE_OPENAI_DEPLOYMENT_NAME=<required>

# Optional
AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING=<optional>
AZURE_EMAIL_SENDER_ADDRESS=<optional>
DATABASE_URL=<optional - defaults to sqlite>
```

## 🐛 Troubleshooting

### Port Issues
If port 8003 is in use, edit `run_server.py` to change:
```python
current_port = 8003  # Change this to your desired port
```

### Template Errors
The application uses a custom `url_for` function for Jinja2 templates. If you see template errors, check that all route names match those defined in `main.py`.

### AI Service Errors
- Ensure Azure credentials are correct in `.env`
- Check Azure service is not suspended
- Verify deployment names match your Azure configuration

## 📞 Support

For issues or questions:
1. Check server console for error messages
2. Review `.env` configuration
3. Ensure all dependencies are installed
4. Create an issue in the repository

---

**FoodXchange** - Advanced AI-Powered Product Analysis Platform