"""
JEET Backend — Analytics API Routes

Aggregated analytics for the Command Center.
All endpoints require admin role (or mentor for cohort-specific views).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.analytics import (
    EngagementDataPoint, EngagementTrendResponse,
    FunnelStep, FunnelResponse,
    ChurnReasonBreakdown, ChurnReasonsResponse,
    PaymentHealthPoint, PaymentHealthResponse,
    CohortDeepDive,
)


router = APIRouter(prefix="/api/admin/analytics", tags=["Analytics"])


@router.get("/engagement-trend", response_model=EngagementTrendResponse)
def get_engagement_trend(
    payload: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=180),
):
    """Daily active students for the last N days."""
    rows = db.execute(text("""
        SELECT
            activity_date,
            COUNT(DISTINCT student_user_id) AS active_students,
            SUM(total_events) AS total_events,
            ROUND(AVG(total_events)::numeric, 2) AS avg_per_student
        FROM v_daily_engagement
        WHERE total_events > 0
          AND activity_date >= CURRENT_DATE - (:days || ' days')::interval
        GROUP BY activity_date
        ORDER BY activity_date
    """), {"days": days}).mappings().all()

    return EngagementTrendResponse(
        period_days=days,
        data=[
            EngagementDataPoint(
                activity_date=r["activity_date"],
                active_students=r["active_students"],
                total_events=int(r["total_events"]),
                avg_events_per_student=float(r["avg_per_student"]),
            )
            for r in rows
        ],
    )


@router.get("/funnel", response_model=FunnelResponse)
def get_funnel(
    payload: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Onboarding funnel:
      Enrolled → Logged in → Completed 1st lesson → Took 1st quiz → Active in week 4
    """
    row = db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM enrollments) AS enrolled,
            (SELECT COUNT(DISTINCT user_id) FROM events WHERE event_type = 'user_login') AS logged_in,
            (SELECT COUNT(DISTINCT user_id) FROM events WHERE event_type = 'lesson_completed') AS completed_lesson,
            (SELECT COUNT(DISTINCT student_user_id) FROM assessments) AS took_quiz,
            (SELECT COUNT(DISTINCT student_user_id)
             FROM v_daily_engagement
             WHERE activity_date >= CURRENT_DATE - INTERVAL '90 days'
               AND activity_date <= CURRENT_DATE - INTERVAL '60 days'
               AND total_events > 0) AS active_week_4
    """)).mappings().fetchone()

    total = row["enrolled"] or 1  # avoid div by 0

    return FunnelResponse(
        total_students=row["enrolled"],
        funnel=[
            FunnelStep(step_name="Enrolled", students=row["enrolled"],
                       conversion_pct=100.0),
            FunnelStep(step_name="Logged In", students=row["logged_in"],
                       conversion_pct=round(row["logged_in"] / total * 100, 2)),
            FunnelStep(step_name="Completed 1st Lesson", students=row["completed_lesson"],
                       conversion_pct=round(row["completed_lesson"] / total * 100, 2)),
            FunnelStep(step_name="Took 1st Quiz", students=row["took_quiz"],
                       conversion_pct=round(row["took_quiz"] / total * 100, 2)),
            FunnelStep(step_name="Active in Week 4", students=row["active_week_4"],
                       conversion_pct=round(row["active_week_4"] / total * 100, 2)),
        ],
    )


@router.get("/churn-reasons", response_model=ChurnReasonsResponse)
def get_churn_reasons(
    payload: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Inferred churn reasons using simple rule classification on at-risk feature view.
    A real system would use the ML model from Day 17 for this — but our rules engine
    gives a strong baseline.
    """
    rows = db.execute(text("""
        WITH churned AS (
            SELECT sf.*
            FROM v_student_features sf
            WHERE sf.enrollment_status = 'churned'
        ),
        classified AS (
            SELECT
                CASE
                    WHEN failed_payments >= 2 THEN 'Financial — payment failures'
                    WHEN avg_score_pct < 35 AND failed_assessments >= 3
                         THEN 'Academic — confidence collapse'
                    WHEN days_since_last_login > 30 AND lesson_completion_rate < 0.3
                         THEN 'Engagement — silent disengagement'
                    WHEN attendance_rate < 0.3 THEN 'Attendance — session no-shows'
                    WHEN late_night_logins > 20 AND lesson_completion_rate < 0.5
                         THEN 'Burnout — overstudy collapse'
                    ELSE 'Other / Unclassified'
                END AS primary_reason
            FROM churned
        )
        SELECT
            primary_reason,
            COUNT(*) AS student_count,
            ROUND(COUNT(*)::numeric / NULLIF(SUM(COUNT(*)) OVER (), 0) * 100, 2) AS percentage
        FROM classified
        GROUP BY primary_reason
        ORDER BY student_count DESC
    """)).mappings().all()

    total = sum(r["student_count"] for r in rows)

    return ChurnReasonsResponse(
        total_churned=total,
        breakdown=[
            ChurnReasonBreakdown(
                primary_reason=r["primary_reason"],
                student_count=r["student_count"],
                percentage=float(r["percentage"] or 0),
            )
            for r in rows
        ],
    )


@router.get("/payment-health", response_model=PaymentHealthResponse)
def get_payment_health(
    payload: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    weeks: int = Query(12, ge=4, le=52),
):
    """Weekly payment success rate."""
    rows = db.execute(text("""
        SELECT
            DATE_TRUNC('week', created_at)::date AS week_start,
            COUNT(*) AS total_attempts,
            COUNT(*) FILTER (WHERE status = 'captured') AS successful,
            COUNT(*) FILTER (WHERE status = 'failed') AS failed,
            ROUND(
                COUNT(*) FILTER (WHERE status = 'captured')::numeric
                / NULLIF(COUNT(*), 0) * 100, 2
            ) AS success_rate,
            COALESCE(SUM(amount_inr) FILTER (WHERE status = 'captured'), 0) AS revenue
        FROM payments
        WHERE created_at >= CURRENT_DATE - (:weeks * 7 || ' days')::interval
        GROUP BY DATE_TRUNC('week', created_at)
        ORDER BY week_start
    """), {"weeks": weeks}).mappings().all()

    return PaymentHealthResponse(
        data=[
            PaymentHealthPoint(
                week_start=r["week_start"],
                total_attempts=r["total_attempts"],
                successful=r["successful"],
                failed=r["failed"],
                success_rate=float(r["success_rate"] or 0),
                revenue_inr=float(r["revenue"]),
            )
            for r in rows
        ],
    )


@router.get("/cohorts/{cohort_id}/deep-dive", response_model=CohortDeepDive)
def get_cohort_deep_dive(
    cohort_id: str,
    payload: dict = Depends(require_role("admin", "mentor")),
    db: Session = Depends(get_db),
):
    """Comprehensive single-cohort report."""

    # Step 1: Cohort metadata
    cohort = db.execute(text("""
        SELECT
            c.id::text AS cohort_id,
            c.name AS cohort_name,
            p.name AS program_name,
            mu.full_name AS mentor_name
        FROM cohorts c
        JOIN programs p ON p.id = c.program_id
        LEFT JOIN users mu ON mu.id = c.mentor_user_id
        WHERE c.id::text = :cid
    """), {"cid": cohort_id}).mappings().fetchone()

    if not cohort:
        raise HTTPException(404, "Cohort not found")

    # Step 2: Enrollment counts (most reliable source)
    enrollment_counts = db.execute(text("""
        SELECT
            COUNT(*) AS total_students,
            COUNT(*) FILTER (WHERE status = 'active') AS active_count,
            COUNT(*) FILTER (WHERE status = 'churned') AS churned_count,
            COUNT(*) FILTER (WHERE status = 'paused') AS paused_count,
            COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled_count
        FROM enrollments
        WHERE cohort_id::text = :cid
    """), {"cid": cohort_id}).mappings().fetchone()

    # Step 3: Engagement + academic averages (from feature view)
    engagement = db.execute(text("""
        SELECT
            COALESCE(AVG(sf.total_logins), 0) AS avg_logins,
            COALESCE(AVG(sf.lesson_completion_rate), 0) AS avg_lesson_completion,
            COALESCE(AVG(sf.attendance_rate), 0) AS avg_attendance,
            COALESCE(AVG(sf.avg_score_pct), 0) AS avg_score,
            COALESCE(SUM(sf.total_assessments), 0) AS total_assessments
        FROM v_student_features sf
        WHERE sf.student_user_id IN (
            SELECT student_user_id::text FROM enrollments WHERE cohort_id::text = :cid
        )
    """), {"cid": cohort_id}).mappings().fetchone()

    # Step 4: Revenue + payment success (subscriptions uses student_user_id)
    revenue = db.execute(text("""
        SELECT
            COALESCE(SUM(pay.amount_inr) FILTER (WHERE pay.status = 'captured'), 0) AS revenue,
            COALESCE(
                COUNT(pay.id) FILTER (WHERE pay.status = 'captured')::numeric
                / NULLIF(COUNT(pay.id), 0) * 100,
                0
            ) AS payment_success_rate,
            COUNT(pay.id) FILTER (WHERE pay.status = 'failed') AS failed_payments
        FROM payments pay
        JOIN subscriptions s ON s.id = pay.subscription_id
        WHERE s.student_user_id IN (
            SELECT student_user_id FROM enrollments WHERE cohort_id::text = :cid
        )
    """), {"cid": cohort_id}).mappings().fetchone()

    # Step 5: At-risk student count
    risk_row = db.execute(text("""
        SELECT COUNT(*) AS at_risk_count
        FROM v_at_risk_students ar
        WHERE ar.risk_tier IN ('urgent', 'critical')
          AND ar.student_user_id IN (
            SELECT student_user_id::text FROM enrollments WHERE cohort_id::text = :cid
          )
    """), {"cid": cohort_id}).mappings().fetchone()

    # Step 6: Intervention counts
    intervention_row = db.execute(text("""
        SELECT
            COUNT(*) AS total_interventions,
            COALESCE(
                COUNT(*) FILTER (WHERE outcome = 'successful')::numeric
                / NULLIF(COUNT(*), 0) * 100,
                0
            ) AS success_rate
        FROM interventions i
        WHERE i.student_user_id IN (
            SELECT student_user_id FROM enrollments WHERE cohort_id::text = :cid
        )
    """), {"cid": cohort_id}).mappings().fetchone()

    # Step 7: Retention at weeks 1/4/12
    retention = db.execute(text("""
        SELECT week_num, retention_pct
        FROM v_cohort_retention
        WHERE cohort_id::text = :cid
          AND week_num IN (1, 4, 12)
        ORDER BY week_num
    """), {"cid": cohort_id}).mappings().all()

    retention_map = {r["week_num"]: float(r["retention_pct"] or 0) for r in retention}

    return CohortDeepDive(
        cohort_id=cohort["cohort_id"],
        cohort_name=cohort["cohort_name"],
        program_name=cohort["program_name"],
        mentor_name=cohort["mentor_name"],
        total_students=enrollment_counts["total_students"] or 0,
        active_count=enrollment_counts["active_count"] or 0,
        churned_count=enrollment_counts["churned_count"] or 0,
        paused_count=enrollment_counts["paused_count"] or 0,
        cancelled_count=enrollment_counts["cancelled_count"] or 0,
        avg_login_count=float(engagement["avg_logins"]),
        avg_lesson_completion_rate=float(engagement["avg_lesson_completion"]),
        avg_attendance_rate=float(engagement["avg_attendance"]),
        avg_score_pct=float(engagement["avg_score"]),
        total_assessments_taken=int(engagement["total_assessments"]),
        total_revenue_inr=float(revenue["revenue"]),
        payment_success_rate=float(revenue["payment_success_rate"]),
        failed_payment_count=revenue["failed_payments"] or 0,
        students_at_risk=risk_row["at_risk_count"] or 0,
        interventions_triggered=intervention_row["total_interventions"] or 0,
        intervention_success_rate=float(intervention_row["success_rate"]),
        week_1_retention=retention_map.get(1, 0.0),
        week_4_retention=retention_map.get(4, 0.0),
        week_12_retention=retention_map.get(12, 0.0),
    )