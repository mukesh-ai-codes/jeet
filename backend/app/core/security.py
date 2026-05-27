"""
JWT and password hashing utilities.

The JWT payload includes:
  - sub: user_id (the JWT standard "subject" claim)
  - email: user's email
  - role: admin | mentor | student | parent
  - institute_id: which institute this user belongs to (B2B tenancy)
  - is_onboarded: has the user completed their onboarding wizard
  - exp: expiry timestamp

The institute_id is hardcoded to "demo-institute-001" until the institutes
table exists. Every JWT-decoded request can rely on this field being present.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Default tenant until institutes table is added (Day 27+ migration)
DEMO_INSTITUTE_ID = "demo-institute-001"

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return _pwd_ctx.verify(plain, hashed)


def create_access_token(
    *,
    user_id: str,
    email: str,
    role: str,
    is_onboarded: bool,
    institute_id: str = DEMO_INSTITUTE_ID,
    expires_minutes: Optional[int] = None,
) -> str:
    """
    Generate a signed JWT for the given user.

    Keyword-only arguments (note the `*,`) prevent accidental positional-arg
    swaps — easy to misorder email/role/institute_id by mistake otherwise.
    """
    expires_minutes = expires_minutes or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "institute_id": institute_id,
        "is_onboarded": is_onboarded,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT. Raises jwt.PyJWTError on any failure
    (expired, malformed, bad signature). Callers should catch and
    convert to HTTP 401.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
