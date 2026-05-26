"""
JEET Backend — Health Check

Used by deployment platforms (Railway, Vercel, k8s) to verify the service is alive.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings


router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
def health_check():
    """Basic liveness check."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
    }


@router.get("/db")
def db_health(db: Session = Depends(get_db)):
    """Verify database connectivity + return key row counts."""
    counts = {}
    for table in ["users", "user_profiles", "enrollments", "events",
                  "assessments", "v_student_features"]:
        try:
            r = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            counts[table] = r
        except Exception as e:
            counts[table] = f"ERROR: {str(e)[:80]}"

    return {
        "status": "ok",
        "database": "connected",
        "row_counts": counts,
    }