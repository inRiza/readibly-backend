from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any
import logging

from database import get_db, Base
from models.user import User
from schemas.auth import UserCreate, UserResponse, Token
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    logger.debug(f"Creating new user with email: {user.email}")
    logger.debug(f"Generated hash for password: {hashed_password}")
    
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    logger.debug(f"Login attempt for email: {form_data.username}")
    logger.debug(f"Password length: {len(form_data.password)}")
    
    # Verify user exists by email
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        logger.debug(f"User not found for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"User found: {user.email}")
    logger.debug(f"Stored hashed password: {user.hashed_password}")
    logger.debug(f"Stored hashed password length: {len(user.hashed_password)}")
    
    # Verify password
    try:
        is_password_correct = verify_password(form_data.password, user.hashed_password)
        logger.debug(f"Password verification result: {is_password_correct}")
        
        if not is_password_correct:
            logger.debug("Password verification failed")
            # Try to hash the input password to see if it matches
            test_hash = get_password_hash(form_data.password)
            logger.debug(f"Test hash of input password: {test_hash}")
            logger.debug(f"Test hash matches stored hash: {test_hash == user.hashed_password}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"Error during password verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    logger.debug("Login successful, token generated")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    return current_user 