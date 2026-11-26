from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import  get_db
from app.logging_config import logger
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.security import (
    verify_access_token, 
    verify_password,
    hash_password,
    create_access_token
    )


router = APIRouter(tags=["Authentication"])

DbSession = Annotated[Session, Depends(get_db)]

bearer_scheme = HTTPBearer()




def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials,
                               Depends(bearer_scheme)],
                               session : DbSession
):
    token = credentials.credentials

    try:
        payload = verify_access_token(token)
        user_id = int(payload["sub"])

    except (ValueError,KeyError,TypeError):
        logger.warning("Authentication failed: invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token",
            headers= {"WWW-Authenticate": "Bearer"}
        )

    user = session.get(User,user_id)

    if user is None:
        logger.warning("Authentication failed : user not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "user not found",
            headers = {"WWW-Authenticate":"Bearer"}
        )

    return user


#-- ROUTES ---
# HOME

@router.post("/register",
        response_model = UserResponse,
        status_code=status.HTTP_201_CREATED
        )

def register_user(
    user_data:UserCreate,
    session : DbSession
):
    existing_user = session.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        logger.warning("Registration failed : email already registered")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= "Email already registered"
        )

    hashed_password= hash_password(user_data.password)

    new_user= User(
        email=user_data.email,
        hashed_password = hashed_password
    )

    session.add(new_user)
    session.commit()
    logger.info("New user registered: %s", new_user.id)
    session.refresh(new_user)

    return new_user

@router.post("/login")
def login(
    user_data : UserCreate,
    session : DbSession
):
    user = session.scalar(
        select(User).where(User.email == user_data.email)
    )

    if not user:
        logger.warning("Login failed: user not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user_data.password,user.hashed_password):
        logger.warning("Login failed : Incorrect password")
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)
    logger.info("user logged in sucessfully : user_id=%s",user.id)
    
    return {
        "access_token": access_token,
        "token_type" : "bearer"
    }
