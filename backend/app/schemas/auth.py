"""
Pydantic schemas for auth endpoints.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    """Public user fields returned to the frontend after auth."""
    id: str
    email: str
    full_name: str
    role: str  # admin | mentor | student | parent
    phone: Optional[str] = None
    institute_id: str
    is_onboarded: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
