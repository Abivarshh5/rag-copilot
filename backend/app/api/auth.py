# 1. imports
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.db.database import SessionLocal
from app.db.models import User
from app.schemas.auth import SignupRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token
)

# 2. router
router = APIRouter(prefix="/auth", tags=["Auth"])

# Security scheme
security = HTTPBearer()

# 3. db dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. request schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

# 5. helper functions
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def email_exists(db: Session, email: str) -> bool:
    return get_user_by_email(db, email) is not None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract and verify JWT token, return current user."""
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# 6. signup endpoint
@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Signup attempt for email: {data.email}")
    if email_exists(db, data.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created successfully"}

# 7. login endpoint
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Login attempt for email: {data.email}")
    user = get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# 8. protected endpoint - get current user
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Protected endpoint - returns current user info."""
    return current_user
