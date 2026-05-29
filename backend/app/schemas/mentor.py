"""
JEET Backend — Mentor Schemas

Mentor "Coach Console" sees cohorts they teach + at-risk students with
the FULL Whisper Layer (more candid than what parents see).
"""

from pydantic import BaseModel
from typing import List, Optional


class CohortSummary(BaseModel):
    cohort_id: str
    name: str
    program_name: str
    total_students: int
    active_students: int
    avg_engagement: Optional[float] = None
    avg_score: Optional[float] = None


class MentorCohortsResponse(BaseModel):
    cohorts: List[CohortSummary]


class AtRiskStudent(BaseModel):
    student_user_id: str
    full_name: str
    grade: int
    target_exam: str
    program_slug: str
    days_since_last_login: int
    lesson_completion_rate: float
    avg_score_pct: float
    attendance_rate: float
    failed_assessments: int
    failed_payments: int
    risk_score: float
    risk_tier: str  # 'urgent' | 'critical' | 'watch' | 'stable' | 'lost'
    enrollment_status: str


class AtRiskListResponse(BaseModel):
    total_at_risk: int
    urgent_count: int
    critical_count: int
    watch_count: int
    students: List[AtRiskStudent]


class WhisperAnnotation(BaseModel):
    """One AI-generated mentor-facing observation."""
    category: str       # 'pattern' | 'concern' | 'recommendation' | 'celebration'
    severity: str       # 'low' | 'medium' | 'high'
    title: str
    detail: str         # Full narrative
    evidence: List[str] # Supporting data points


class StudentWhisperResponse(BaseModel):
    student_user_id: str
    full_name: str
    risk_tier: str
    risk_score: float
    annotations: List[WhisperAnnotation]
    suggested_intervention: Optional[str] = None
    model_reasons: List[str] = []