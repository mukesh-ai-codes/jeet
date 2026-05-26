"""
JEET Backend — Auth Schemas (Pydantic models)

These define the SHAPE of requests/responses for auth endpoints.
Pydantic auto-validates incoming JSON and serializes outgoing data.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Login payload: email + password."""
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=128)


class TokenResponse(BaseModel):
    """Response after successful login or signup."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until token expiry

    # User info (so frontend can render immediately without extra call)
    user_id: str
    email: str
    full_name: str
    role: str


class CurrentUserResponse(BaseModel):
    """Response for /api/auth/me — current authenticated user."""
    user_id: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    is_active: bool
    email_verified: bool