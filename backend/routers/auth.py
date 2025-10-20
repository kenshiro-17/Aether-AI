from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import models
from database import get_db
import auth_service
from pydantic import BaseModel

router = APIRouter()

from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

@router.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check existing
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new
    hashed_pwd = auth_service.get_password_hash(user.password)
    
    # Handle optional email
    email_value = user.email
    if not email_value or not email_value.strip():
        email_value = None
        
    new_user = models.User(
        username=user.username, 
        email=email_value,
        hashed_password=hashed_pwd,
        full_name=user.full_name,
        avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=" + user.username
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        avatar_url=new_user.avatar_url
    )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/auth/me", response_model=UserResponse)
async def read_users_me(current_user: models.User = Depends(auth_service.get_current_user)):
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url
    )
