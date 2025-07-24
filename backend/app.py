from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import bcrypt
import os
from dotenv import load_dotenv
from azure.ai.openai import OpenAIClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

app = FastAPI(title="FoodXchange API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Azure OpenAI
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")

openai_client = None
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY:
    openai_client = OpenAIClient(
        endpoint=AZURE_OPENAI_ENDPOINT,
        credential=AzureKeyCredential(AZURE_OPENAI_KEY)
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database simulation (replace with Azure Cosmos DB later)
fake_users_db = {
    "demo@foodxchange.com": {
        "email": "demo@foodxchange.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "full_name": "Demo User",
        "company": "FoodXchange Demo"
    }
}

fake_suppliers_db = [
    {
        "id": 1,
        "name": "Mediterranean Delights",
        "location": "Greece",
        "products": ["Olive Oil", "Feta Cheese", "Olives"],
        "response_rate": 92,
        "last_contact": "2024-01-20",
        "status": "active"
    },
    {
        "id": 2,
        "name": "Italian Fine Foods",
        "location": "Italy", 
        "products": ["Pasta", "Tomatoes", "Mozzarella"],
        "response_rate": 87,
        "last_contact": "2024-01-18",
        "status": "active"
    },
    {
        "id": 3,
        "name": "Spanish Imports Co",
        "location": "Spain",
        "products": ["Jamón", "Manchego", "Saffron"],
        "response_rate": 78,
        "last_contact": "2024-01-15",
        "status": "pending"
    }
]

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    email: EmailStr
    full_name: str
    company: str

class UserInDB(User):
    hashed_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Supplier(BaseModel):
    id: int
    name: str
    location: str
    products: List[str]
    response_rate: int
    last_contact: str
    status: str

class EmailAnalysis(BaseModel):
    email_content: str

class EmailAnalysisResponse(BaseModel):
    classification: str
    confidence: float
    suggested_action: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_user(email: str):
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return UserInDB(**user_dict)

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to FoodXchange API"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/suppliers", response_model=List[Supplier])
async def get_suppliers(current_user: User = Depends(get_current_user)):
    return fake_suppliers_db

@app.get("/suppliers/search")
async def search_suppliers(
    query: str,
    current_user: User = Depends(get_current_user)
):
    # Simple search implementation
    results = []
    for supplier in fake_suppliers_db:
        if query.lower() in supplier["name"].lower() or \
           any(query.lower() in product.lower() for product in supplier["products"]):
            results.append(supplier)
    return results

@app.post("/analyze-email", response_model=EmailAnalysisResponse)
async def analyze_email(
    email_data: EmailAnalysis,
    current_user: User = Depends(get_current_user)
):
    if not openai_client:
        raise HTTPException(status_code=500, detail="Azure OpenAI is not configured.")
    prompt = f"""
    You are an AI assistant for a food trading platform. Analyze the following supplier email and classify it as one of: interested, not_interested, needs_followup. Also provide a confidence score (0-1) and a suggested action.
    Email:
    {email_data.email_content}
    Respond in JSON with keys: classification, confidence, suggested_action.
    """
    response = openai_client.get_chat_completions(
        deployment_id=AZURE_OPENAI_DEPLOYMENT,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.2
    )
    content = response.choices[0].message.content
    import json
    try:
        result = json.loads(content)
        return EmailAnalysisResponse(**result)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse OpenAI response.")

@app.get("/dashboard-stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    return {
        "total_suppliers": 20532,
        "active_suppliers": len([s for s in fake_suppliers_db if s["status"] == "active"]),
        "pending_emails": 89,
        "response_rate": 72.5,
        "new_this_week": 152
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 