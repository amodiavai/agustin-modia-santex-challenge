import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class AuthService:
    def __init__(self):
        try:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        except Exception as e:
            # Fallback if bcrypt has issues
            print(f"Warning: bcrypt initialization issue: {e}")
            self.pwd_context = None
            
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Credentials from environment variables
        self.ADMIN_USER = os.getenv("ADMIN_USER", "admin-gd")
        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-in-production")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        if self.pwd_context:
            return self.pwd_context.verify(plain_password, hashed_password)
        else:
            # Simple fallback comparison if bcrypt fails
            return plain_password == hashed_password

    def authenticate_user(self, username: str, password: str) -> bool:
        if username != self.ADMIN_USER:
            return False
        # Direct password comparison for simplicity
        return password == self.ADMIN_PASSWORD

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None

    def login(self, username: str, password: str) -> Token:
        if not self.authenticate_user(username, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")