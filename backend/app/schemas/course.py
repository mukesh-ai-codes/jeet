"""
JEET Backend — Course Schemas
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProgramSummary(BaseModel):
    id: str
    slug: str
    name: str
    description: Optional[str] = None
    price_inr: float
    duration_months: int
    features: Optional[List[str]] = None
    is_active: bool


class SubjectSummary(BaseModel):
    id: str
    slug: str
    name: str
    description: Optional[str] = None


class LessonSummary(BaseModel):
    id: str
    subject_name: str
    chapter: str
    title: str
    duration_minutes: int
    difficulty_level: int
    sequence_order: int


class LessonDetail(BaseModel):
    id: str
    subject_id: str
    subject_name: str
    chapter: str
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    notes_url: Optional[str] = None
    duration_minutes: int
    difficulty_level: int
    sequence_order: int
    is_published: bool


class ChapterSummary(BaseModel):
    subject_slug: str
    chapter_name: str
    total_lessons: int
    avg_difficulty: float
    total_duration_minutes: int


class LessonListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    lessons: List[LessonSummary]


class RecommendedLesson(BaseModel):
    lesson: LessonSummary
    reason: str  # Why this is recommended


class RecommendationResponse(BaseModel):
    student_user_id: str
    recommendations: List[RecommendedLesson]


class WeakChapter(BaseModel):
    subject_name: str
    chapter: str
    quizzes_attempted: int
    avg_score: float
    last_attempted_at: Optional[datetime] = None


class WeakChaptersResponse(BaseModel):
    student_user_id: str
    weak_chapters: List[WeakChapter]


class TrackEventRequest(BaseModel):
    event_type: str  # 'lesson_started' | 'lesson_completed' | 'lesson_abandoned' etc.
    event_data: Optional[dict] = None


class TrackEventResponse(BaseModel):
    event_id: str
    accepted: bool

# =============================================================
# DAILY PLAN (Day 13)
# =============================================================

class DailyPlanItem(BaseModel):
    """One slot in the student's daily plan."""
    slot: str  # 'review' | 'learn' | 'practice'
    label: str  # "Review your weak chapter" — short human-readable
    reason: str  # Why this was picked, shown as a sub-line
    lesson: LessonSummary


class DailyPlanResponse(BaseModel):
    """3-slot personalized daily plan. Some slots may be missing if data is thin."""
    student_user_id: str
    items: List[DailyPlanItem]
    generated_at: datetime
