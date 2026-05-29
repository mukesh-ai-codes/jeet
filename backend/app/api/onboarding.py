"""
Onboarding endpoints.

Currently:
  POST /api/onboarding/admin/configure  — Receives admin's 8-question payload

The endpoint validates shape, logs the data (so we can see it in dev), and
returns success. Persistence to an institutes table is deferred to Day 27
when the multi-tenancy schema lands.

This decoupling matters: the frontend ships a real, validated payload
that matches the future schema, so when the institutes table arrives
the only change needed is one INSERT statement here.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.deps import get_current_user

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# Source of truth for Day 27 institutes-table write. Maps wizard labels ->
# DB exam_type enums. Defined now so the distinction is captured at onboarding;
# not yet wired to a DB write (no institutes table until Day 27).
EXAM_LABEL_TO_ENUM = {
    "JEE Main": "jee_main",
    "JEE Advanced": "jee_advanced",
    "NEET": "neet_ug",
    "Foundation": "foundation",
    "Other": "board",
}


class AdminConfigurePayload(BaseModel):
    """Shape submitted from the admin onboarding wizard."""

    institute_name: str = Field(min_length=2, max_length=120)
    institute_size: str  # "1-2" | "3-5" | "6-15" | "16-50" | "50+"
    primary_exams: list[str]  # subset of ["JEE Main","JEE Advanced","NEET","Foundation","Other"]
    cohort_count: int = Field(ge=0, le=10000)
    mentor_count: int = Field(ge=0, le=10000)
    review_tool_today: str  # "spreadsheets" | "whatsapp" | "lms" | "nothing_structured"
    biggest_pain: str  # "silent_dropouts" | ... | "revenue_leakage"
    go_live_window: str  # "this_week" | "this_month" | "exploring"
    notes: Optional[str] = Field(default=None, max_length=500)


@router.post("/admin/configure")
def configure_admin_institute(
    payload: AdminConfigurePayload,
    current_user: dict = Depends(get_current_user),
):
    """
    Accept the admin's onboarding payload.

    For Day 12: validate shape, log it, return ok. The actual config-to-DB
    write will be wired up on Day 27 when we add the institutes table.
    """
    # Role gate — only admins should hit this endpoint
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only institute admins can configure an institute.",
        )

    user_id = current_user.get("id") or current_user.get("sub")
    email = current_user.get("email", "<unknown>")

    print("=" * 60)
    print(f"📝 Admin onboarding received")
    print(f"   User:       {email} ({user_id})")
    print(f"   Institute:  {payload.institute_name}")
    print(f"   Size:       {payload.institute_size}")
    print(f"   Exams:      {', '.join(payload.primary_exams)}")
    print(f"   -> enums:   {[EXAM_LABEL_TO_ENUM.get(e, '?') for e in payload.primary_exams]}")
    print(f"   Cohorts:    {payload.cohort_count}")
    print(f"   Mentors:    {payload.mentor_count}")
    print(f"   Review:     {payload.review_tool_today}")
    print(f"   Pain:       {payload.biggest_pain}")
    print(f"   Go-live:    {payload.go_live_window}")
    if payload.notes:
        print(f"   Notes:      {payload.notes}")
    print("=" * 60)

    return {
        "status": "ok",
        "message": "Institute configuration received. Activating workspace.",
    }
