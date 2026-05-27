"""
Authentication endpoints.

- POST /api/auth/login           — JSON login, returns JWT
- POST /api/auth/token           — OAuth2 form login (for Swagger), returns JWT
- GET  /api/auth/me              — Returns the current user from JWT
- POST /api/auth/complete-onboarding  — Marks user onboarded, returns new JWT
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    verify_password,
    DEMO_INSTITUTE_ID,
)
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _fetch_user_by_email(db: Session, email: str) -> dict | None:
    """Return user row as dict, or None if not found."""
    row = db.execute(
        text(
            """
            SELECT id, email, password_hash, full_name, role, phone, is_onboarded
            FROM users
            WHERE email = :email
            """
        ),
        {"email": email},
    ).mappings().first()
    return dict(row) if row else None


def _build_login_response(user: dict) -> LoginResponse:
    """Helper to build the standard login response from a user row."""
    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user["role"],
        is_onboarded=user["is_onboarded"],
        institute_id=DEMO_INSTITUTE_ID,
    )
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=str(user["id"]),
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            phone=user.get("phone"),
            institute_id=DEMO_INSTITUTE_ID,
            is_onboarded=user["is_onboarded"],
        ),
    )


@router.post("/login", response_model=LoginResponse)
def login_json(payload: LoginRequest, db: Session = Depends(get_db)):
    """JSON-body login. Used by the frontend."""
    user = _fetch_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return _build_login_response(user)


@router.post("/token", response_model=LoginResponse)
def login_oauth_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 form-body login. Used by Swagger UI's Authorize button."""
    user = _fetch_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return _build_login_response(user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return UserResponse(
        id=str(current_user["id"]),
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        phone=current_user.get("phone"),
        institute_id=current_user.get("institute_id", DEMO_INSTITUTE_ID),
        is_onboarded=current_user["is_onboarded"],
    )


@router.post("/complete-onboarding", response_model=LoginResponse)
def complete_onboarding(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark the current user as onboarded and return a refreshed JWT.

    The frontend should replace its stored token with the new one so
    subsequent requests carry is_onboarded=true.
    """
    result = db.execute(
        text(
            """
            UPDATE users
            SET is_onboarded = TRUE
            WHERE id = :user_id
            RETURNING id, email, password_hash, full_name, role, phone, is_onboarded
            """
        ),
        {"user_id": current_user["id"]},
    ).mappings().first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.commit()
    return _build_login_response(dict(result))
