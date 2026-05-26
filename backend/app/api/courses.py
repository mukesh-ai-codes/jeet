"""
JEET Backend — Course/Learning API Routes

Endpoints for content discovery and lesson tracking.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user_payload, require_role
from app.schemas.course import (
    ProgramSummary, SubjectSummary, LessonSummary, LessonDetail,
    ChapterSummary, LessonListResponse, RecommendedLesson,
    RecommendationResponse, WeakChapter, WeakChaptersResponse,
    TrackEventRequest, TrackEventResponse,
)


router = APIRouter(prefix="/api/courses", tags=["Courses"])


# =============================================================
# PROGRAMS (Plans)
# =============================================================
@router.get("/programs", response_model=list[ProgramSummary])
def list_programs(db: Session = Depends(get_db)):
    """Public — anyone can see available plans."""
    rows = db.execute(text("""
        SELECT id::text, slug, name, price_inr, duration_months, is_active
        FROM programs
        WHERE is_active = TRUE
        ORDER BY price_inr ASC
    """)).mappings().all()

    return [
        ProgramSummary(
            id=r["id"],
            slug=r["slug"],
            name=r["name"],
            description=None,
            price_inr=float(r["price_inr"]),
            duration_months=r["duration_months"],
            features=None,
            is_active=r["is_active"],
        )
        for r in rows
    ]


@router.get("/programs/{slug}", response_model=ProgramSummary)
def get_program(slug: str, db: Session = Depends(get_db)):
    """Single program details."""
    row = db.execute(text("""
        SELECT id::text, slug, name, price_inr, duration_months, is_active
        FROM programs
        WHERE slug = :slug
        LIMIT 1
    """), {"slug": slug}).mappings().fetchone()

    if not row:
        raise HTTPException(404, "Program not found")

    return ProgramSummary(
        id=row["id"],
        slug=row["slug"],
        name=row["name"],
        description=None,
        price_inr=float(row["price_inr"]),
        duration_months=row["duration_months"],
        features=None,
        is_active=row["is_active"],
    )


# =============================================================
# SUBJECTS
# =============================================================
@router.get("/subjects", response_model=list[SubjectSummary])
def list_subjects(db: Session = Depends(get_db)):
    """Public — list all subjects."""
    rows = db.execute(text("""
        SELECT id::text, slug, name, description
        FROM subjects
        ORDER BY name
    """)).mappings().all()

    return [
        SubjectSummary(
            id=r["id"], slug=r["slug"], name=r["name"], description=r["description"],
        )
        for r in rows
    ]


@router.get("/subjects/{subject_slug}/chapters", response_model=list[ChapterSummary])
def get_chapters_for_subject(subject_slug: str, db: Session = Depends(get_db)):
    """Chapter list within a subject, with lesson counts."""
    rows = db.execute(text("""
        SELECT
            s.slug AS subject_slug,
            l.chapter AS chapter_name,
            COUNT(*) AS total_lessons,
            ROUND(AVG(l.difficulty_level)::numeric, 2) AS avg_difficulty,
            SUM(l.duration_minutes) AS total_duration
        FROM lessons l
        JOIN subjects s ON s.id = l.subject_id
        WHERE s.slug = :slug AND l.is_published = TRUE
        GROUP BY s.slug, l.chapter
        ORDER BY MIN(l.sequence_order)
    """), {"slug": subject_slug}).mappings().all()

    if not rows:
        raise HTTPException(404, "Subject not found or has no chapters")

    return [
        ChapterSummary(
            subject_slug=r["subject_slug"],
            chapter_name=r["chapter_name"],
            total_lessons=r["total_lessons"],
            avg_difficulty=float(r["avg_difficulty"]),
            total_duration_minutes=int(r["total_duration"]),
        )
        for r in rows
    ]


# =============================================================
# LESSONS
# =============================================================
@router.get("/lessons", response_model=LessonListResponse)
def list_lessons(
    db: Session = Depends(get_db),
    subject_slug: str | None = Query(None, description="Filter by subject slug"),
    chapter: str | None = Query(None, description="Filter by chapter name"),
    difficulty: int | None = Query(None, ge=1, le=5, description="Filter by difficulty"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Paginated lesson listing with filters."""
    where_clauses = ["l.is_published = TRUE"]
    params = {"limit": page_size, "offset": (page - 1) * page_size}

    if subject_slug:
        where_clauses.append("s.slug = :subject_slug")
        params["subject_slug"] = subject_slug
    if chapter:
        where_clauses.append("l.chapter = :chapter")
        params["chapter"] = chapter
    if difficulty is not None:
        where_clauses.append("l.difficulty_level = :difficulty")
        params["difficulty"] = difficulty

    where_sql = " AND ".join(where_clauses)

    # Total count
    total = db.execute(text(f"""
        SELECT COUNT(*) FROM lessons l
        JOIN subjects s ON s.id = l.subject_id
        WHERE {where_sql}
    """), params).scalar()

    # Page
    rows = db.execute(text(f"""
        SELECT
            l.id::text,
            s.name AS subject_name,
            l.chapter,
            l.title,
            l.duration_minutes,
            l.difficulty_level,
            l.sequence_order
        FROM lessons l
        JOIN subjects s ON s.id = l.subject_id
        WHERE {where_sql}
        ORDER BY l.sequence_order
        LIMIT :limit OFFSET :offset
    """), params).mappings().all()

    return LessonListResponse(
        total=total,
        page=page,
        page_size=page_size,
        lessons=[
            LessonSummary(
                id=r["id"],
                subject_name=r["subject_name"],
                chapter=r["chapter"],
                title=r["title"],
                duration_minutes=r["duration_minutes"],
                difficulty_level=r["difficulty_level"],
                sequence_order=r["sequence_order"],
            )
            for r in rows
        ],
    )


@router.get("/lessons/{lesson_id}", response_model=LessonDetail)
def get_lesson(lesson_id: str, db: Session = Depends(get_db)):
    """Single lesson with full details."""
    row = db.execute(text("""
        SELECT
            l.id::text, l.subject_id::text, s.name AS subject_name,
            l.chapter, l.title, l.description,
            l.video_url, l.notes_url, l.duration_minutes,
            l.difficulty_level, l.sequence_order, l.is_published
        FROM lessons l
        JOIN subjects s ON s.id = l.subject_id
        WHERE l.id = :lid
        LIMIT 1
    """), {"lid": lesson_id}).mappings().fetchone()

    if not row:
        raise HTTPException(404, "Lesson not found")

    return LessonDetail(**dict(row))