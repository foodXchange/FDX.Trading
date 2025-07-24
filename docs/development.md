# Development Guide

## Project Structure
```
FoodXchange/
├── backend/
│   ├── app_integrated.py    # Main application
│   ├── database.py          # Database operations
│   ├── email_service.py     # Email handling
│   ├── ai_analytics.py      # AI features
│   └── tests/               # Unit tests
├── frontend/
│   ├── src/
│   │   ├── pages/          # React pages
│   │   ├── components/     # Reusable components
│   │   └── services/       # API calls
│   └── public/
└── docs/
```

## Adding Features

### Backend
1. Create new endpoint in `app_integrated.py`
2. Add business logic in separate module
3. Update API documentation
4. Write tests

### Frontend
1. Create component in `components/`
2. Add route if needed
3. Connect to API
4. Update user guide

## Testing
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
npm test
```

## Code Style
- Python: Follow PEP 8
- JavaScript: Use ESLint
- Comments for complex logic
- Docstrings for functions 