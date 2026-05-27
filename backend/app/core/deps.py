"""
FastAPI dependencies for auth and role-based access.

Exposes:
  get_current_user_payload  — returns the raw JWT payload dict (used by older endpoints)
  get_current_user          — returns the user row from DB + payload claims (preferred)
  require_role(*roles)      — gates an endpoint to specific roles

The two get_current_user_* variants exist for backwards compatibility:
older endpoints (Days 7-10) use _payload; new endpoints (Day 12+) use the
full user fetch which includes is_onboarded fresh from the DB.
"""

from typing import Callable

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token, DEMO_INSTITUTE_ID


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.split(" ", 1)[1].strip()


def _decode_or_401(token: str) -> dict:
    try:
        return decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_payload(
    authorization: str | None = Header(default=None),
) -> dict:
    """
    Lightweight dependency: decodes the JWT and returns the payload dict.

    Use this when an endpoint only needs the role / user_id from the token
    and does NOT need fresh DB data. Cheaper than get_current_user because
    it skips a SELECT.

    Returns a dict with keys: sub, email, role, institute_id, is_onboarded, iat, exp
    """
    token = _extract_token(authorization)
    payload = _decode_or_401(token)

    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    # Backwards-compat: older code expects 'user_id' key; new code uses 'sub'
    payload["user_id"] = payload["sub"]
    # Defensive: always provide institute_id even if old token didn't have it
    payload.setdefault("institute_id", DEMO_INSTITUTE_ID)
    return payload


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    """
    Full dependency: decodes JWT, fetches the user row from the DB.

    Use this when you need authoritative user fields (is_onboarded, full_name)
    that may have changed since the JWT was issued.

    Returns a dict combining DB columns and JWT claims:
      id, email, full_name, role, phone, is_onboarded, institute_id
    """
    token = _extract_token(authorization)
    payload = _decode_or_401(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    row = db.execute(
        text(
            """
            SELECT id, email, full_name, role, phone, is_onboarded
            FROM users
            WHERE id = :user_id
            """
        ),
        {"user_id": user_id},
    ).mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    user = dict(row)
    user["institute_id"] = payload.get("institute_id", DEMO_INSTITUTE_ID)
    return user


def require_role(*allowed_roles: str) -> Callable:
    """
    Dependency factory: gates an endpoint to one or more roles.

    Accepts either a JWT payload (from get_current_user_payload) or a full
    user dict (from get_current_user) — both expose a 'role' key.

    Usage:
        @router.get("/admin/something")
        def handler(user = Depends(require_role("admin"))):
            ...
    """
    def _check_role(payload: dict = Depends(get_current_user_payload)) -> dict:
        user_role = payload.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}",
            )
        return payload
    return _check_role
