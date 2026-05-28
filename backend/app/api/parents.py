"""
JEET Backend — Parent Routes

Endpoints for parent dashboards.
Parents see their child's progress with softer Whisper Layer messaging.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.parent import (
    ChildSummary, ParentChildrenResponse,
    WhisperInsight, ParentDashboard,
    MentorInfo, InterventionSummary,
)


router = APIRouter(prefix="/api/parents", tags=["Parents"])


@router.get("/me/children", response_model=ParentChildrenResponse)
def get_my_children(
    payload: dict = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """List children linked to this parent via families table."""
    user_id = payload["sub"]

    rows = db.execute(text("""
        SELECT
            u.id::text AS student_user_id,
            u.full_name,
            up.grade,
            up.target_exam,
            p.name AS program_name,
            e.status AS enrollment_status,
            f.relationship
        FROM families f
        JOIN users u ON u.id = f.student_user_id
        JOIN user_profiles up ON up.user_id = u.id
        JOIN enrollments e ON e.student_user_id = u.id
        JOIN programs p ON p.id = e.program_id
        WHERE f.parent_user_id::text = :uid
        ORDER BY u.full_name
    """), {"uid": user_id}).mappings().all()

    return ParentChildrenResponse(children=[
        ChildSummary(
            student_user_id=r["student_user_id"],
            full_name=r["full_name"],
            grade=r["grade"],
            target_exam=r["target_exam"],
            program_name=r["program_name"],
            enrollment_status=r["enrollment_status"],
            relationship=r["relationship"],
        )
        for r in rows
    ])


@router.get("/me/children/{student_id}/dashboard", response_model=ParentDashboard)
def get_child_dashboard(
    student_id: str,
    payload: dict = Depends(require_role("parent")),
    db: Session = Depends(get_db),
):
    """
    Parent's view of one child.
    Includes a softer Whisper Layer (encouragement-first messaging).
    """
    user_id = payload["sub"]

    # Verify this parent owns this child
    link = db.execute(text("""
        SELECT 1 FROM families
        WHERE parent_user_id::text = :pid AND student_user_id::text = :sid
        LIMIT 1
    """), {"pid": user_id, "sid": student_id}).fetchone()

    if not link:
        raise HTTPException(403, "You are not authorized to view this child's dashboard.")

    # Fetch features
    row = db.execute(text("""
        SELECT
            sf.*,
            (SELECT MAX(created_at) FROM events
             WHERE user_id::text = sf.student_user_id AND event_type = 'user_login') AS last_login_at,
            p.name AS program_name
        FROM v_student_features sf
        JOIN enrollments e ON e.student_user_id::uuid = sf.student_user_id::uuid
        JOIN programs p ON p.id = e.program_id
        WHERE sf.student_user_id = :sid
        LIMIT 1
    """), {"sid": student_id}).mappings().fetchone()

    if not row:
        raise HTTPException(404, "Child data not found")

    insights = _generate_parent_insights(row)

    # ---- Mentor info (from the child's active cohort) ----
    mentor_row = db.execute(text("""
        SELECT
            u.full_name AS mentor_name,
            u.email AS mentor_email,
            c.name AS cohort_name
        FROM enrollments e
        JOIN cohorts c ON c.id = e.cohort_id
        LEFT JOIN users u ON u.id = c.mentor_user_id
        WHERE e.student_user_id::text = :sid
          AND e.status = 'active'
        LIMIT 1
    """), {"sid": student_id}).mappings().fetchone()

    mentor = None
    if mentor_row and mentor_row["mentor_name"]:
        mentor = MentorInfo(
            full_name=mentor_row["mentor_name"],
            email=mentor_row["mentor_email"],
            cohort_name=mentor_row["cohort_name"],
        )

    # ---- Recent interventions (parent-visible touchpoints) ----
    # Show only human-meaningful types; hide raw system nudges from parents.
    intervention_rows = db.execute(text("""
        SELECT
            i.id::text AS id,
            i.intervention_type,
            i.notes,
            i.outcome,
            i.trigger_reason,
            i.created_at,
            i.resolved_at,
            u.full_name AS initiator_name
        FROM interventions i
        JOIN users u ON u.id = i.initiated_by_user_id
        WHERE i.student_user_id::text = :sid
          AND i.intervention_type IN (
            'mentor_call', 'mentor_message', 'parent_call',
            'parent_email', 'wellness_check', 'tutor_session'
          )
        ORDER BY i.created_at DESC
        LIMIT 3
    """), {"sid": student_id}).mappings().all()

    recent_interventions = [
        InterventionSummary(
            id=r["id"],
            intervention_type=r["intervention_type"],
            notes=r["notes"],
            outcome=r["outcome"],
            trigger_reason=r["trigger_reason"],
            created_at=r["created_at"],
            resolved_at=r["resolved_at"],
            initiator_name=r["initiator_name"],
        )
        for r in intervention_rows
    ]

    return ParentDashboard(
        child_name=row["full_name"],
        grade=row["grade"],
        target_exam=row["target_exam"],
        program_name=row["program_name"],
        days_active=int(row["days_active"]),
        enrollment_status=row["enrollment_status"],
        total_logins=row["total_logins"],
        days_since_last_login=int(row["days_since_last_login"]),
        lesson_completion_rate=float(row["lesson_completion_rate"]),
        avg_score_pct=float(row["avg_score_pct"]),
        attendance_rate=float(row["attendance_rate"]),
        insights=insights,
        last_login_at=row["last_login_at"],
        mentor=mentor,
        recent_interventions=recent_interventions,
    )


def _generate_parent_insights(row) -> list:
    """
    Softer Whisper Layer for parents.
    Same signals as mentor view, but framed encouragingly + actionably.
    """
    insights = []

    # Engagement
    if row["days_since_last_login"] > 14:
        insights.append(WhisperInsight(
            severity="urgent",
            category="engagement",
            message=f"Your child hasn't logged in for {int(row['days_since_last_login'])} days. "
                    f"This may be a good moment for a supportive check-in.",
            metric_value=float(row["days_since_last_login"]),
        ))
    elif row["days_since_last_login"] > 5:
        insights.append(WhisperInsight(
            severity="watch",
            category="engagement",
            message=f"Login activity has slowed in the last {int(row['days_since_last_login'])} days.",
            metric_value=float(row["days_since_last_login"]),
        ))

    # Academic
    if float(row["avg_score_pct"]) >= 65:
        insights.append(WhisperInsight(
            severity="positive",
            category="academic",
            message=f"Quiz scores are strong (avg {float(row['avg_score_pct']):.0f}%). "
                    f"Your child is on a good track.",
            metric_value=float(row["avg_score_pct"]),
        ))
    elif float(row["avg_score_pct"]) < 40:
        insights.append(WhisperInsight(
            severity="watch",
            category="academic",
            message=f"Quiz scores are below average ({float(row['avg_score_pct']):.0f}%). "
                    f"A conversation with their mentor may help.",
            metric_value=float(row["avg_score_pct"]),
        ))

    # Attendance
    if float(row["attendance_rate"]) >= 0.85:
        insights.append(WhisperInsight(
            severity="positive",
            category="engagement",
            message=f"Live session attendance is excellent ({float(row['attendance_rate'])*100:.0f}%).",
            metric_value=float(row["attendance_rate"]),
        ))
    elif float(row["attendance_rate"]) < 0.5:
        insights.append(WhisperInsight(
            severity="watch",
            category="engagement",
            message=f"Live session attendance is low ({float(row['attendance_rate'])*100:.0f}%). "
                    f"Ask if the schedule fits.",
            metric_value=float(row["attendance_rate"]),
        ))

    # Late-night usage — gentle framing for parents
    if row["late_night_logins"] > 10:
        insights.append(WhisperInsight(
            severity="watch",
            category="wellness",
            message=f"Your child has had {row['late_night_logins']} late-night study sessions. "
                    f"Consider encouraging better sleep — it improves retention.",
            metric_value=float(row["late_night_logins"]),
        ))

    # Financial
    if row["failed_payments"] >= 1:
        insights.append(WhisperInsight(
            severity="urgent",
            category="financial",
            message=f"There were {row['failed_payments']} payment issues recently. "
                    f"Please check your payment method to ensure uninterrupted access.",
            metric_value=float(row["failed_payments"]),
        ))

    if not insights:
        insights.append(WhisperInsight(
            severity="info",
            category="engagement",
            message="Things are going well. Keep encouraging consistent effort.",
        ))

    return insights