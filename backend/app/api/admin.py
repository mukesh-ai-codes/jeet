"""
JEET Backend — Admin (Command Center) Routes

Endpoints for platform-wide analytics:
  GET /api/admin/overview            — top-level KPIs
  GET /api/admin/cohorts/retention   — retention curves
  GET /api/admin/revenue             — revenue breakdown
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.admin import (
    PlatformOverview, CohortRetentionPoint, CohortRetentionResponse,
    RevenueByPlan, AdminRevenueResponse,
)


router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/overview", response_model=PlatformOverview)
def get_platform_overview(
    payload: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Top-level platform KPIs."""

    row = db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM users) AS total_users,
            (SELECT COUNT(*) FROM users WHERE role='student') AS total_students,
            (SELECT COUNT(*) FROM users WHERE role='mentor') AS total_mentors,
            (SELECT COUNT(*) FROM users WHERE role='parent') AS total_parents,

            (SELECT COUNT(*) FROM subscriptions WHERE status='active') AS active_subs,
            (SELECT COUNT(*) FROM subscriptions WHERE status='churned') AS churned_subs,
            (SELECT COUNT(*) FROM subscriptions WHERE status='paused') AS paused_subs,

            (SELECT COALESCE(SUM(amount_inr), 0) FROM payments WHERE status='captured') AS total_revenue,
            (SELECT COALESCE(SUM(amount_inr), 0) FROM payments
                WHERE status='captured' AND paid_at >= NOW() - INTERVAL '30 days') AS recent_revenue,
            (SELECT COUNT(*) FILTER (WHERE status='captured')::float
                    / NULLIF(COUNT(*), 0) FROM payments) AS payment_success,

            (SELECT COUNT(*) FROM events) AS total_events,
            (SELECT COUNT(*) FROM lessons) AS total_lessons,
            (SELECT COUNT(*) FROM assessments) AS total_assessments
    """)).mappings().fetchone()

    total_students = row["total_students"]
    active = row["active_subs"]
    retention = (active / total_students * 100) if total_students else 0.0

    return PlatformOverview(
        total_users=row["total_users"],
        total_students=total_students,
        total_mentors=row["total_mentors"],
        total_parents=row["total_parents"],
        active_subscriptions=active,
        churned_subscriptions=row["churned_subs"],
        paused_subscriptions=row["paused_subs"],
        retention_pct=round(retention, 2),
        total_revenue_inr=float(row["total_revenue"]),
        total_revenue_crore=round(float(row["total_revenue"]) / 10_000_000, 2),
        revenue_last_30_days_inr=float(row["recent_revenue"]),
        payment_success_rate=round(float(row["payment_success"] or 0), 4),
        total_events_generated=row["total_events"],
        total_lessons_offered=row["total_lessons"],
        total_assessments_taken=row["total_assessments"],
    )


@router.get("/cohorts/retention", response_model=CohortRetentionResponse)
def get_cohort_retention(
    payload: dict = Depends(require_role("admin", "mentor")),
    db: Session = Depends(get_db),
    limit_cohorts: int = 10,
):
    """Cohort retention curves from the materialized view."""

    rows = db.execute(text("""
        SELECT cohort_id, cohort_name, week_num, retention_pct, active_students
        FROM v_cohort_retention
        WHERE cohort_id IN (
            SELECT DISTINCT cohort_id FROM v_cohort_retention LIMIT :limit
        )
        ORDER BY cohort_name, week_num
    """), {"limit": limit_cohorts}).mappings().all()

    return CohortRetentionResponse(cohorts=[
        CohortRetentionPoint(
            cohort_id=r["cohort_id"],
            cohort_name=r["cohort_name"],
            week_num=r["week_num"],
            retention_pct=float(r["retention_pct"] or 0),
            active_students=r["active_students"] or 0,
        )
        for r in rows
    ])


@router.get("/revenue", response_model=AdminRevenueResponse)
def get_revenue_dashboard(
    payload: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Revenue breakdown by plan."""

    rows = db.execute(text("""
        SELECT
            p.name AS plan_name,
            p.slug AS plan_slug,
            COUNT(DISTINCT s.id) AS subscribers,
            COALESCE(SUM(pay.amount_inr) FILTER (WHERE pay.status='captured'), 0) AS revenue,
            COALESCE(AVG(pay.amount_inr) FILTER (WHERE pay.status='captured'), 0) AS arpu
        FROM programs p
        LEFT JOIN subscriptions s ON s.program_id = p.id
        LEFT JOIN payments pay ON pay.subscription_id = s.id
        GROUP BY p.id, p.name, p.slug
        ORDER BY p.price_inr
    """)).mappings().all()

    totals = db.execute(text("""
        SELECT
            COALESCE(SUM(amount_inr) FILTER (WHERE status='captured'), 0) AS captured,
            COALESCE(SUM(amount_inr) FILTER (WHERE status='failed'), 0) AS failed
        FROM payments
    """)).mappings().fetchone()

    return AdminRevenueResponse(
        by_plan=[
            RevenueByPlan(
                plan_name=r["plan_name"],
                plan_slug=r["plan_slug"],
                subscribers=r["subscribers"],
                total_revenue_inr=float(r["revenue"]),
                avg_revenue_per_user=float(r["arpu"]),
            )
            for r in rows
        ],
        total_captured_inr=float(totals["captured"]),
        total_failed_attempts_inr=float(totals["failed"]),
    )