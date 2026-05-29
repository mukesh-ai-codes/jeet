"""
JEET Backend — Student Schemas

Pydantic models for student-facing API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# =============================================================
# STUDENT DASHBOARD
# =============================================================

class StudentProfileBlock(BaseModel):
    full_name: str
    grade: int
    target_exam: str
    primary_goal: Optional[str] = None
    motivation_score: Optional[int] = None
    weak_subjects: List[str] = []


class EnrollmentBlock(BaseModel):
    program_name: str
    program_slug: str
    cohort_name: Optional[str] = None
    mentor_name: Optional[str] = None
    enrolled_at: datetime
    days_active: int
    status: str  # active / churned / cancelled / paused


class EngagementBlock(BaseModel):
    total_logins: int
    unique_active_days: int
    days_since_last_login: int
    active_day_ratio: float
    sunday_logins: int
    late_night_logins: int


class LearningProgressBlock(BaseModel):
    lessons_started: int
    lessons_completed: int
    lessons_abandoned: int
    lesson_completion_rate: float
    notes_downloaded: int
    sessions_attended: int
    sessions_scheduled: int
    attendance_rate: float


class AssessmentSummaryBlock(BaseModel):
    total_assessments: int
    avg_score_pct: float
    best_score_pct: float
    worst_score_pct: float
    recent_avg_score_pct: float
    failed_assessments: int
    strong_assessments: int
    score_volatility: float


class RecentAssessment(BaseModel):
    title: str
    subject: str
    chapter: Optional[str] = None
    score: float
    max_score: float
    percentage: float
    submitted_at: datetime


class StudentDashboard(BaseModel):
    """Full dashboard payload sent to the student's home screen."""
    profile: StudentProfileBlock
    enrollment: EnrollmentBlock
    engagement: EngagementBlock
    learning: LearningProgressBlock
    assessments: AssessmentSummaryBlock
    recent_assessments: List[RecentAssessment]
    risk_tier: str    # real backend tier: stable|watch|critical|urgent|lost
    risk_score: float # 0-100, same scale as the mentor view


# =============================================================
# STREAK CALENDAR
# =============================================================

class DailyActivity(BaseModel):
    activity_date: date
    logins: int
    lessons_completed: int
    quizzes_completed: int
    total_events: int
    was_active: bool  # True if any activity happened


class StreakResponse(BaseModel):
    current_streak: int    # consecutive active days ending today
    longest_streak: int    # all-time best
    total_active_days: int
    daily_activity: List[DailyActivity]