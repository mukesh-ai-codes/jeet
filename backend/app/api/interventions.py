"""
JEET Backend — Intervention API Routes

The Pulse Engine v1 — where mentors and admins log + analyze interventions.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.analytics import (
    InterventionCreate, InterventionRecord, InterventionListResponse,
    InterventionEffectivenessPoint, InterventionEffectivenessResponse,
)


router = APIRouter(tags=["Interventions"])


# =============================================================
# CREATE INTERVENTION (Mentor logs a call/message)
# =============================================================
@router.post("/api/mentors/interventions", response_model=InterventionRecord)
def create_intervention(
    body: InterventionCreate,
    payload: dict = Depends(require_role("mentor", "admin")),
    db: Session = Depends(get_db),
):
    """Log a new intervention. Mentor records what they did + why."""
    user_id = payload["sub"]

    # Validate intervention type
    valid_types = {
        "mentor_call", "mentor_message", "parent_call", "parent_email",
        "system_nudge", "discount_offer", "tutor_session", "wellness_check",
    }
    if body.intervention_type not in valid_types:
        raise HTTPException(400, f"Invalid type. Allowed: {sorted(valid_types)}")

    # Verify student exists
    student = db.execute(text("""
        SELECT id, full_name FROM users WHERE id = :sid AND role = 'student'
    """), {"sid": body.student_user_id}).mappings().fetchone()
    if not student:
        raise HTTPException(404, "Student not found")

    # Capture current risk score (snapshot)
    risk_row = db.execute(text("""
        SELECT risk_score FROM v_at_risk_students WHERE student_user_id = :sid
    """), {"sid": body.student_user_id}).mappings().fetchone()
    risk_before = float(risk_row["risk_score"]) if risk_row else 0.0

    # Insert
    iv_id = str(uuid.uuid4())
    db.execute(text("""
        INSERT INTO interventions (
            id, student_user_id, initiated_by_user_id,
            intervention_type, trigger_reason, notes,
            outcome, risk_score_before
        ) VALUES (
            :id, :sid, :uid, :itype, :reason, :notes, 'pending', :risk
        )
    """), {
        "id": iv_id,
        "sid": body.student_user_id,
        "uid": user_id,
        "itype": body.intervention_type,
        "reason": body.trigger_reason,
        "notes": body.notes,
        "risk": risk_before,
    })
    db.commit()

    # Fetch + return
    initiator = db.execute(text(
        "SELECT full_name FROM users WHERE id = :uid"
    ), {"uid": user_id}).mappings().fetchone()

    row = db.execute(text("""
        SELECT * FROM interventions WHERE id = :id
    """), {"id": iv_id}).mappings().fetchone()

    return InterventionRecord(
        id=str(row["id"]),
        student_user_id=str(row["student_user_id"]),
        student_name=student["full_name"],
        initiated_by_user_id=str(row["initiated_by_user_id"]),
        initiated_by_name=initiator["full_name"] if initiator else "Unknown",
        intervention_type=row["intervention_type"],
        trigger_reason=row["trigger_reason"],
        notes=row["notes"],
        outcome=row["outcome"],
        risk_score_before=float(row["risk_score_before"]) if row["risk_score_before"] else None,
        risk_score_after=float(row["risk_score_after"]) if row["risk_score_after"] else None,
        created_at=row["created_at"],
        resolved_at=row["resolved_at"],
    )


# =============================================================
# MENTOR INTERVENTION HISTORY
# =============================================================
@router.get("/api/mentors/me/interventions", response_model=InterventionListResponse)
def list_my_interventions(
    payload: dict = Depends(require_role("mentor", "admin")),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
):
    """All interventions initiated by current user."""
    user_id = payload["sub"]

    rows = db.execute(text("""
        SELECT
            i.id::text,
            i.student_user_id::text,
            su.full_name AS student_name,
            i.initiated_by_user_id::text,
            iu.full_name AS initiated_by_name,
            i.intervention_type,
            i.trigger_reason,
            i.notes,
            i.outcome,
            i.risk_score_before,
            i.risk_score_after,
            i.created_at,
            i.resolved_at
        FROM interventions i
        JOIN users su ON su.id = i.student_user_id
        JOIN users iu ON iu.id = i.initiated_by_user_id
        WHERE i.initiated_by_user_id::text = :uid
        ORDER BY i.created_at DESC
        LIMIT :limit
    """), {"uid": user_id, "limit": limit}).mappings().all()

    return InterventionListResponse(
        total=len(rows),
        interventions=[
            InterventionRecord(
                id=r["id"],
                student_user_id=r["student_user_id"],
                student_name=r["student_name"],
                initiated_by_user_id=r["initiated_by_user_id"],
                initiated_by_name=r["initiated_by_name"],
                intervention_type=r["intervention_type"],
                trigger_reason=r["trigger_reason"],
                notes=r["notes"],
                outcome=r["outcome"],
                risk_score_before=float(r["risk_score_before"]) if r["risk_score_before"] else None,
                risk_score_after=float(r["risk_score_after"]) if r["risk_score_after"] else None,
                created_at=r["created_at"],
                resolved_at=r["resolved_at"],
            )
            for r in rows
        ],
    )


# =============================================================
# INTERVENTION EFFECTIVENESS (Admin)
# =============================================================
@router.get("/api/admin/interventions/effectiveness",
            response_model=InterventionEffectivenessResponse)
def get_intervention_effectiveness(
    payload: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Did our interventions actually save students? Breakdown by type."""

    rows = db.execute(text("""
        SELECT
            intervention_type,
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE outcome = 'successful') AS successful,
            COUNT(*) FILTER (WHERE outcome = 'no_response') AS no_response,
            COUNT(*) FILTER (WHERE outcome = 'failed') AS failed,
            ROUND(
                COUNT(*) FILTER (WHERE outcome = 'successful')::numeric
                / NULLIF(COUNT(*), 0) * 100, 2
            ) AS success_rate,
            ROUND(
                AVG(risk_score_before - risk_score_after) FILTER
                    (WHERE risk_score_before IS NOT NULL AND risk_score_after IS NOT NULL),
                2
            ) AS avg_risk_reduction
        FROM interventions
        GROUP BY intervention_type
        ORDER BY total DESC
    """)).mappings().all()

    totals = db.execute(text("""
        SELECT
            COUNT(*) AS total,
            ROUND(
                COUNT(*) FILTER (WHERE outcome = 'successful')::numeric
                / NULLIF(COUNT(*), 0) * 100, 2
            ) AS overall_success_rate
        FROM interventions
    """)).mappings().fetchone()

    return InterventionEffectivenessResponse(
        total_interventions=totals["total"] or 0,
        overall_success_rate=float(totals["overall_success_rate"] or 0),
        by_type=[
            InterventionEffectivenessPoint(
                intervention_type=r["intervention_type"],
                total_count=r["total"],
                successful_count=r["successful"],
                no_response_count=r["no_response"],
                failed_count=r["failed"],
                success_rate=float(r["success_rate"] or 0),
                avg_risk_reduction=float(r["avg_risk_reduction"] or 0),
            )
            for r in rows
        ],
    )