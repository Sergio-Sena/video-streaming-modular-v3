from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    refreshToken: str
    user: dict

class RefreshTokenRequest(BaseModel):
    refreshToken: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

class TokenData(BaseModel):
    sub: str
    user_id: str
    name: str
    exp: datetime
    type: Optional[str] = "access"