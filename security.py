from pwdlib import PasswordHash  
from datetime import datetime, timedelta, timezone
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes= ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload= {
        "sub":str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload, SECRET_KEY,algorithm=ALGORITHM
    )

    return token


def verify_access_token(token:str) -> dict:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )

        return payload

    except jwt.InvalidTokenError:
        raise ValueError("Invalid or expired token")


password_hash = PasswordHash.recommended()


def hash_password(password : str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password,hashed_password)
