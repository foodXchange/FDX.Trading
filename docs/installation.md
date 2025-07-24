# Installation Guide

## System Requirements
- Python 3.9 or higher
- Node.js 16 or higher
- 8GB RAM minimum
- Windows/Mac/Linux

## Backend Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and fill in your values:
- Azure OpenAI credentials
- Cosmos DB connection
- Email settings

### 4. Initialize Database
```bash
python init_database.py
```

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure API Endpoint
Edit `src/config.js`:
```javascript
export const API_URL = 'http://localhost:8000';
```

### 3. Start Development Server
```bash
npm start
```

## Troubleshooting
- [Common Issues](./troubleshooting.md)
- [FAQ](./faq.md) 