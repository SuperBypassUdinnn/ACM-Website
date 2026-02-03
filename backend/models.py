"""
Pydantic Models

Data validation models for API requests and responses.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class ChatReq(BaseModel):
    """Chat request model"""
    message: str
    session_id: str


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    name: str = "User"
    plan: str = "free"


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: dict
    client: dict
    api_key: str
