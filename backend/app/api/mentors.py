"""
JEET Backend — Mentor (Coach Console) Routes

Endpoints used by the Coach Console:
  GET /api/mentors/me/cohorts            — list cohorts I teach
  GET /api/mentors/me/at-risk-students   — student alerts (the Whisper Layer)
  GET /api/mentors/me/students/{student_id}/whisper  — detailed AI insights
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.mentor import (
    CohortSummary, MentorCohortsResponse,
    AtRiskStudent, AtRiskListResponse,
    WhisperAnnotation, StudentWhisperResponse,
)


router = APIRouter(prefix="/api/mentors", tags=["Mentors"])


@router.get("/me/cohorts", response_model=MentorCohortsResponse)
def get_my_cohorts(
    payload: dict = Depends(require_role("mentor", "admin")),
    db: Session = Depends(get_db),
):
    user_id = payload["sub"]

    rows = db.execute(text("""
        SELECT
            c.id::text AS cohort_id,
            c.name,
            p.name AS program_name,
            COUNT(e.id) AS total_students,
            COUNT(e.id) FILTER (WHERE e.status = 'active') AS active_students,
            AVG(sf.avg_engagement_score) AS avg_engagement,
            AVG(sf.avg_score_pct) AS avg_score
        FROM cohorts c
        JOIN programs p ON p.id = c.program_id
        LEFT JOIN enrollments e ON e.cohort_id = c.id
        LEFT JOIN v_student_features sf ON sf.student_user_id = e.student_user_id::text
        WHERE c.mentor_user_id::text = :uid
        GROUP BY c.id, c.name, p.name
        ORDER BY c.name
    """), {"uid": user_id}).mappings().all()

    return MentorCohortsResponse(cohorts=[
        CohortSummary(
            cohort_id=r["cohort_id"],
            name=r["name"],
            program_name=r["program_name"],
            total_students=r["total_students"],
            active_students=r["active_students"],
            avg_engagement=float(r["avg_engagement"]) if r["avg_engagement"] else None,
            avg_score=float(r["avg_score"]) if r["avg_score"] else None,
        )
        for r in rows
    ])


@router.get("/me/at-risk-students", response_model=AtRiskListResponse)
def get_at_risk_students(
    payload: dict = Depends(require_role("mentor", "admin")),
    db: Session = Depends(get_db),
    limit: int = 150,
):
    """
    The Whisper Layer — students needing intervention, ranked by risk.
    Mentors see only their own cohort's students (admins see all).
    """
    user_id = payload["sub"]
    role = payload["role"]

    if role == "admin":
        # Admin sees everyone
        where_clause = "1=1"
        params = {"limit": limit}
    else:
        # Mentor sees only students in cohorts they teach
        where_clause = """
            student_user_id IN (
                SELECT e.student_user_id::text
                FROM enrollments e
                JOIN cohorts c ON c.id = e.cohort_id
                WHERE c.mentor_user_id::text = :uid
            )
        """
        params = {"uid": user_id, "limit": limit}

    # Summary counts: computed over the FULL at-risk population (no LIMIT) so the
    # mentor's summary strip is always truthful, independent of the display cap.
    count_rows = db.execute(text(f"""
        SELECT risk_tier, COUNT(*) AS n
        FROM v_at_risk_students
        WHERE {where_clause}
          AND risk_tier IN ('urgent', 'critical', 'watch')
        GROUP BY risk_tier
    """), params).mappings().all()
    counts = {cr["risk_tier"]: int(cr["n"]) for cr in count_rows}
    urgent = counts.get("urgent", 0)
    critical = counts.get("critical", 0)
    watch = counts.get("watch", 0)
    total_at_risk = urgent + critical + watch

    # Display queue: focused triage list, capped. Worst-first by risk score.
    rows = db.execute(text(f"""
        SELECT *
        FROM v_at_risk_students
        WHERE {where_clause}
          AND risk_tier IN ('urgent', 'critical', 'watch')
        ORDER BY risk_score DESC
        LIMIT :limit
    """), params).mappings().all()

    return AtRiskListResponse(
        total_at_risk=total_at_risk,
        urgent_count=urgent,
        critical_count=critical,
        watch_count=watch,
        students=[
            AtRiskStudent(
                student_user_id=r["student_user_id"],
                full_name=r["full_name"],
                grade=r["grade"],
                target_exam=r["target_exam"],
                program_slug=r["program_slug"],
                days_since_last_login=int(r["days_since_last_login"]),
                lesson_completion_rate=float(r["lesson_completion_rate"]),
                avg_score_pct=float(r["avg_score_pct"]),
                attendance_rate=float(r["attendance_rate"]),
                failed_assessments=r["failed_assessments"],
                failed_payments=r["failed_payments"],
                risk_score=float(r["risk_score"]),
                risk_tier=r["risk_tier"],
                enrollment_status=r["enrollment_status"],
            )
            for r in rows
        ],
    )


@router.get("/me/students/{student_id}/whisper", response_model=StudentWhisperResponse)
def get_student_whisper(
    student_id: str,
    payload: dict = Depends(require_role("mentor", "admin")),
    db: Session = Depends(get_db),
):
    """
    The detailed Whisper Layer for ONE student.
    Generates AI-style annotations based on the feature view.
    """
    row = db.execute(text("""
        SELECT * FROM v_at_risk_students WHERE student_user_id = :sid
        UNION ALL
        SELECT
            sf.student_user_id,
            sf.full_name,
            sf.grade,
            sf.target_exam,
            sf.program_slug,
            sf.days_since_last_login,
            sf.lesson_completion_rate,
            sf.avg_score_pct,
            sf.attendance_rate,
            sf.failed_assessments,
            sf.late_night_logins,
            sf.failed_payments,
            sf.enrollment_status,
            0::numeric AS risk_score,
            'stable' AS risk_tier
        FROM v_student_features sf
        WHERE sf.student_user_id = :sid
          AND NOT EXISTS (SELECT 1 FROM v_at_risk_students WHERE student_user_id = :sid)
        LIMIT 1
    """), {"sid": student_id}).mappings().fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    # Generate annotations based on rules (pre-LLM Whisper Layer v1)
    annotations = _generate_whisper_annotations(row)
    suggested = _suggest_intervention(row)

    return StudentWhisperResponse(
        student_user_id=row["student_user_id"],
        full_name=row["full_name"],
        risk_tier=row["risk_tier"],
        risk_score=float(row["risk_score"]),
        annotations=annotations,
        suggested_intervention=suggested,
    )


# =============================================================
# WHISPER LAYER RULES ENGINE (Day 8 v1 — will be LLM-enhanced in Day 22)
# =============================================================
def _generate_whisper_annotations(row) -> list:
    """Rule-based AI annotations. To be replaced with LLM-generated in Day 22."""
    annotations = []

    # Login pattern
    if row["days_since_last_login"] > 14:
        annotations.append(WhisperAnnotation(
            category="concern",
            severity="high",
            title="Extended absence detected",
            detail=f"Student hasn't logged in for {int(row['days_since_last_login'])} days. "
                   f"This is the strongest churn signal in our data.",
            evidence=[f"days_since_last_login = {int(row['days_since_last_login'])}"],
        ))
    elif row["days_since_last_login"] > 7:
        annotations.append(WhisperAnnotation(
            category="pattern",
            severity="medium",
            title="Weakening engagement",
            detail=f"Login gap of {int(row['days_since_last_login'])} days suggests momentum is slipping. "
                   f"A check-in call now can usually prevent escalation.",
            evidence=[f"days_since_last_login = {int(row['days_since_last_login'])}"],
        ))

    # Academic
    if float(row["avg_score_pct"]) < 35 and row["failed_assessments"] >= 3:
        annotations.append(WhisperAnnotation(
            category="concern",
            severity="high",
            title="Confidence collapse risk",
            detail=f"Avg score is {float(row['avg_score_pct']):.1f}% with {row['failed_assessments']} failed quizzes. "
                   f"This pattern often precedes academic-driven churn. Consider a one-on-one fundamentals session.",
            evidence=[
                f"avg_score_pct = {float(row['avg_score_pct']):.1f}",
                f"failed_assessments = {row['failed_assessments']}",
            ],
        ))

    # Attendance
    if float(row["attendance_rate"]) < 0.4:
        annotations.append(WhisperAnnotation(
            category="pattern",
            severity="medium",
            title="Skipping live sessions",
            detail=f"Only {float(row['attendance_rate'])*100:.0f}% live session attendance. "
                   f"They may be self-studying — verify rather than assuming disengagement.",
            evidence=[f"attendance_rate = {float(row['attendance_rate']):.2f}"],
        ))

    # Late-night usage
    if row["late_night_logins"] > 15:
        annotations.append(WhisperAnnotation(
            category="concern",
            severity="medium",
            title="Late-night study pattern — burnout risk",
            detail=f"{row['late_night_logins']} sessions between 11pm-2am. "
                   f"Recommend a wellness check; this often precedes burnout collapse.",
            evidence=[f"late_night_logins = {row['late_night_logins']}"],
        ))

    # Financial
    if row["failed_payments"] >= 2:
        annotations.append(WhisperAnnotation(
            category="concern",
            severity="high",
            title="Payment friction with parent",
            detail=f"{row['failed_payments']} failed payment attempts. "
                   f"This is financial churn risk — different intervention than academic. "
                   f"Reach out to parent, not student.",
            evidence=[f"failed_payments = {row['failed_payments']}"],
        ))

    # Positive patterns
    if float(row["lesson_completion_rate"]) > 0.85 and float(row["avg_score_pct"]) > 70:
        annotations.append(WhisperAnnotation(
            category="celebration",
            severity="low",
            title="High performer — protect this trajectory",
            detail=f"Completion {float(row['lesson_completion_rate'])*100:.0f}%, "
                   f"avg score {float(row['avg_score_pct']):.0f}%. "
                   f"Schedule a recognition message; positive reinforcement compounds.",
            evidence=[
                f"lesson_completion_rate = {float(row['lesson_completion_rate']):.2f}",
                f"avg_score_pct = {float(row['avg_score_pct']):.1f}",
            ],
        ))

    if not annotations:
        annotations.append(WhisperAnnotation(
            category="pattern",
            severity="low",
            title="Stable engagement",
            detail="No immediate concerns. Student is following a healthy pattern.",
            evidence=[],
        ))

    return annotations


def _suggest_intervention(row) -> str:
    """Suggested next action for the mentor."""
    if row["failed_payments"] >= 2:
        return "Contact parent regarding payment issues — financial churn risk."
    if row["days_since_last_login"] > 14:
        return "Personalized re-engagement call. Acknowledge gap without judgement."
    if float(row["avg_score_pct"]) < 35:
        return "Schedule 1-on-1 fundamentals review. Avoid more quizzes for 5 days."
    if row["late_night_logins"] > 15:
        return "Wellness check-in. Discuss study schedule and sleep."
    if float(row["attendance_rate"]) < 0.4:
        return "Ask why they're missing live sessions — could be timing or content fit."
    return "No urgent action needed. Keep weekly touchpoint."