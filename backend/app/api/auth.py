"""
JEET Backend — Authentication Routes

Endpoints:
  POST /api/auth/login   — exchange email+password for JWT
  GET  /api/auth/me      — get current user info from JWT
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.deps import get_current_user_payload
from app.schemas.auth import LoginRequest, TokenResponse, CurrentUserResponse


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT.

    Note: In our synthetic data, all users have password "demo123!"
    (bcrypt hash stored in users.password_hash).
    """
    # Fetch user by email
    result = db.execute(
        text("""
            SELECT id::text, email, full_name, role, password_hash,
                   is_active, email_verified
            FROM users
            WHERE LOWER(email) = LOWER(:email)
            LIMIT 1
        """),
        {"email": payload.email},
    ).fetchone()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_id, email, full_name, role, password_hash, is_active, email_verified = result

    # Verify password
    if not verify_password(payload.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Generate token
    access_token = create_access_token(subject=user_id, role=role)

    # Update last_login_at
    db.execute(
        text("UPDATE users SET last_login_at = NOW() WHERE id::text = :uid"),
        {"uid": user_id},
    )
    db.commit()

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user_id,
        email=email,
        full_name=full_name,
        role=role,
    )


@router.get("/me", response_model=CurrentUserResponse)
def get_me(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    """Return the currently authenticated user's details."""
    user_id = payload.get("sub")

    result = db.execute(
        text("""
            SELECT id::text, email, full_name, role, phone,
                   is_active, email_verified
            FROM users
            WHERE id::text = :uid
            LIMIT 1
        """),
        {"uid": user_id},
    ).fetchone()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    uid, email, full_name, role, phone, is_active, email_verified = result

    return CurrentUserResponse(
        user_id=uid,
        email=email,
        full_name=full_name,
        role=role,
        phone=phone,
        is_active=is_active,
        email_verified=email_verified,
    )
@router.post("/token", response_model=TokenResponse, include_in_schema=False)
def login_via_oauth2_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login (used by Swagger UI's Authorize button).

    Accepts form-encoded `username` (= email) + `password`.
    Returns the same TokenResponse as /login.
    """
    # Reuse the logic by building a LoginRequest from the OAuth2 form
    payload = LoginRequest(email=form_data.username, password=form_data.password)
    return login(payload=payload, db=db)