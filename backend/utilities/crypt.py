from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
from jose import JWTError, jwt
from schema.user import CustomerView
from dotenv import load_dotenv
import os

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str)-> CustomerView|None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str= payload.get("name")
        email: str= payload.get("user_email")
        user_id : int = payload.get("id")
        phone_number: str = payload.get("phone_number")
        if email is None:
            return None
        return CustomerView(id=user_id,name=name,user_email=email,phone_number=phone_number)
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None