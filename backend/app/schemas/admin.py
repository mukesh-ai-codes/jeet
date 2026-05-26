"""
JEET Backend — Admin Schemas

Admin "Command Center" sees platform-wide KPIs + retention + revenue.
"""

from pydantic import BaseModel
from typing import List
from datetime import date


class PlatformOverview(BaseModel):
    """Top-level KPIs for the admin overview screen."""
    total_users: int
    total_students: int
    total_mentors: int
    total_parents: int
    active_subscriptions: int
    churned_subscriptions: int
    paused_subscriptions: int
    retention_pct: float

    total_revenue_inr: float
    total_revenue_crore: float
    revenue_last_30_days_inr: float
    payment_success_rate: float

    total_events_generated: int
    total_lessons_offered: int
    total_assessments_taken: int


class CohortRetentionPoint(BaseModel):
    cohort_id: str
    cohort_name: str
    week_num: int
    retention_pct: float
    active_students: int


class CohortRetentionResponse(BaseModel):
    cohorts: List[CohortRetentionPoint]


class RevenueByPlan(BaseModel):
    plan_name: str
    plan_slug: str
    subscribers: int
    total_revenue_inr: float
    avg_revenue_per_user: float


class AdminRevenueResponse(BaseModel):
    by_plan: List[RevenueByPlan]
    total_captured_inr: float
    total_failed_attempts_inr: float