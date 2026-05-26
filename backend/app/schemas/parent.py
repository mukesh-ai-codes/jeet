"""
JEET Backend — Parent Schemas

Parent dashboard sees their child's progress with a softer tone +
includes the Whisper Layer summary (AI insights for parents).
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChildSummary(BaseModel):
    student_user_id: str
    full_name: str
    grade: int
    target_exam: str
    program_name: str
    enrollment_status: str
    relationship: str  # 'father' or 'mother' or 'guardian'


class ParentChildrenResponse(BaseModel):
    children: List[ChildSummary]


class WhisperInsight(BaseModel):
    """A single AI-generated insight about the student."""
    severity: str       # 'positive' | 'info' | 'watch' | 'urgent'
    category: str       # 'engagement' | 'academic' | 'wellness' | 'financial'
    message: str        # Human-readable insight
    metric_value: Optional[float] = None


class ParentDashboard(BaseModel):
    """What parents see about their child's progress."""
    child_name: str
    grade: int
    target_exam: str
    program_name: str
    days_active: int
    enrollment_status: str

    # Headline numbers
    total_logins: int
    days_since_last_login: int
    lesson_completion_rate: float
    avg_score_pct: float
    attendance_rate: float

    # The Whisper Layer (softer tone for parents)
    insights: List[WhisperInsight]

    # Recent activity
    last_login_at: Optional[datetime] = None
    # =============================================================
# (Already defined above: ChildSummary, ParentChildrenResponse, WhisperInsight, ParentDashboard)
# =============================================================