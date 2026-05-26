"""
JEET Backend — Analytics & Intervention Schemas
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


# =============================================================
# ENGAGEMENT TREND
# =============================================================
class EngagementDataPoint(BaseModel):
    activity_date: date
    active_students: int
    total_events: int
    avg_events_per_student: float


class EngagementTrendResponse(BaseModel):
    period_days: int
    data: List[EngagementDataPoint]


# =============================================================
# FUNNEL
# =============================================================
class FunnelStep(BaseModel):
    step_name: str
    students: int
    conversion_pct: float


class FunnelResponse(BaseModel):
    total_students: int
    funnel: List[FunnelStep]


# =============================================================
# CHURN REASONS
# =============================================================
class ChurnReasonBreakdown(BaseModel):
    primary_reason: str
    student_count: int
    percentage: float


class ChurnReasonsResponse(BaseModel):
    total_churned: int
    breakdown: List[ChurnReasonBreakdown]


# =============================================================
# PAYMENT HEALTH
# =============================================================
class PaymentHealthPoint(BaseModel):
    week_start: date
    total_attempts: int
    successful: int
    failed: int
    success_rate: float
    revenue_inr: float


class PaymentHealthResponse(BaseModel):
    data: List[PaymentHealthPoint]


# =============================================================
# INTERVENTIONS
# =============================================================
class InterventionCreate(BaseModel):
    student_user_id: str
    intervention_type: str   # mentor_call / mentor_message / etc.
    trigger_reason: str
    notes: Optional[str] = None


class InterventionRecord(BaseModel):
    id: str
    student_user_id: str
    student_name: str
    initiated_by_user_id: str
    initiated_by_name: str
    intervention_type: str
    trigger_reason: str
    notes: Optional[str] = None
    outcome: Optional[str] = None
    risk_score_before: Optional[float] = None
    risk_score_after: Optional[float] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class InterventionListResponse(BaseModel):
    total: int
    interventions: List[InterventionRecord]


# =============================================================
# INTERVENTION EFFECTIVENESS
# =============================================================
class InterventionEffectivenessPoint(BaseModel):
    intervention_type: str
    total_count: int
    successful_count: int
    no_response_count: int
    failed_count: int
    success_rate: float
    avg_risk_reduction: float  # How much did risk_score drop after intervention?


class InterventionEffectivenessResponse(BaseModel):
    total_interventions: int
    overall_success_rate: float
    by_type: List[InterventionEffectivenessPoint]


# =============================================================
# COHORT DEEP DIVE
# =============================================================
class CohortDeepDive(BaseModel):
    cohort_id: str
    cohort_name: str
    program_name: str
    mentor_name: Optional[str] = None

    # Demographics
    total_students: int
    active_count: int
    churned_count: int
    paused_count: int
    cancelled_count: int

    # Engagement
    avg_login_count: float
    avg_lesson_completion_rate: float
    avg_attendance_rate: float

    # Academic
    avg_score_pct: float
    total_assessments_taken: int

    # Financial
    total_revenue_inr: float
    payment_success_rate: float
    failed_payment_count: int

    # Risk
    students_at_risk: int
    interventions_triggered: int
    intervention_success_rate: float

    # Retention curve
    week_1_retention: float
    week_4_retention: float
    week_12_retention: float