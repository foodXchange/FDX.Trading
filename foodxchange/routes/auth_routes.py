"""
Authentication routes for FoodXchange
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from foodxchange.database import get_db
from foodxchange.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SessionAuth,
    get_current_user_context
)
from foodxchange.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, for API access"""
    user = authenticate_user(db, form_data.username, form_data.password)
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


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission"""
    user = authenticate_user(db, email, password)
    if not user:
        return RedirectResponse(
            url="/login?error=Invalid+email+or+password",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Create session
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    SessionAuth.create_session(response, user)
    return response


@router.get("/logout")
async def logout(request: Request):
    """Logout and clear session"""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    SessionAuth.clear_session(response)
    return response


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    company: str = Form(None),
    db: Session = Depends(get_db)
):
    """Handle registration form submission"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return RedirectResponse(
            url="/register?error=Email+already+registered",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # Create new user
    user = User(
        name=name,
        email=email,
        hashed_password=get_password_hash(password),
        company=company,
        is_active=True,
        is_admin=False  # First user could be made admin
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Auto-login after registration
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    SessionAuth.create_session(response, user)
    return response


def include_auth_routes(app):
    """Include authentication routes in the main app"""
    app.include_router(router)
    
    # Add FullStory test route
    @app.get("/fullstory-test", response_class=HTMLResponse)
    async def fullstory_test_page(request: Request):
        """FullStory tracking test page"""
        from foodxchange.templates import templates
        return templates.TemplateResponse("fullstory_test.html", {"request": request})
    
    # Override the login POST route
    @app.post("/login")
    async def login_page_post(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
    ):
        """Handle login form submission from the main login page"""
        user = authenticate_user(db, email, password)
        if not user:
            return RedirectResponse(
                url="/login?error=Invalid+email+or+password",
                status_code=status.HTTP_303_SEE_OTHER
            )
        
        # Create session
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        SessionAuth.create_session(response, user)
        return response