"""
JEET Backend — Student API Routes

Endpoints used by the student dashboard:
  GET /api/students/me/dashboard      — full home screen payload
  GET /api/students/me/assessments    — assessment history
  GET /api/students/me/streak         — daily activity streak
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.student import (
    StudentDashboard, StudentProfileBlock, EnrollmentBlock,
    EngagementBlock, LearningProgressBlock, AssessmentSummaryBlock,
    RecentAssessment, StreakResponse, DailyActivity,
)


router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("/me/dashboard", response_model=StudentDashboard)
def get_my_dashboard(
    payload: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Full dashboard payload — single query against v_student_features."""
    user_id = payload["sub"]

    # 1. Pull feature row (40 columns)
    row = db.execute(text("""
        SELECT * FROM v_student_features WHERE student_user_id = :uid
    """), {"uid": user_id}).mappings().fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student features not found. Have feature views been refreshed?",
        )

    # 2. Pull profile detail (weak_subjects, primary_goal — not in v_student_features)
    profile_row = db.execute(text("""
        SELECT primary_goal, motivation_score, weak_subjects
        FROM user_profiles
        WHERE user_id = :uid
    """), {"uid": user_id}).mappings().fetchone()

    # 3. Pull mentor + cohort + program names
    enrollment_row = db.execute(text("""
        SELECT
            p.name AS program_name,
            c.name AS cohort_name,
            mu.full_name AS mentor_name,
            e.enrolled_at
        FROM enrollments e
        JOIN programs p ON p.id = e.program_id
        LEFT JOIN cohorts c ON c.id = e.cohort_id
        LEFT JOIN users mu ON mu.id = c.mentor_user_id
        WHERE e.student_user_id = :uid
        ORDER BY e.enrolled_at DESC
        LIMIT 1
    """), {"uid": user_id}).mappings().fetchone()

    # 4. Recent assessments
    recent_rows = db.execute(text("""
        SELECT
            a.title,
            s.name AS subject,
            a.chapter,
            a.score,
            a.max_score,
            ROUND((a.score::numeric / a.max_score) * 100, 2) AS percentage,
            a.submitted_at
        FROM assessments a
        JOIN subjects s ON s.id = a.subject_id
        WHERE a.student_user_id = :uid
        ORDER BY a.submitted_at DESC
        LIMIT 5
    """), {"uid": user_id}).mappings().all()

    # 5. Compose response
    return StudentDashboard(
        profile=StudentProfileBlock(
            full_name=row["full_name"],
            grade=row["grade"],
            target_exam=row["target_exam"],
            primary_goal=profile_row["primary_goal"] if profile_row else None,
            motivation_score=profile_row["motivation_score"] if profile_row else None,
            weak_subjects=profile_row["weak_subjects"] if profile_row and profile_row["weak_subjects"] else [],
        ),
        enrollment=EnrollmentBlock(
            program_name=enrollment_row["program_name"] if enrollment_row else "Unknown",
            program_slug=row["program_slug"],
            cohort_name=enrollment_row["cohort_name"] if enrollment_row else None,
            mentor_name=enrollment_row["mentor_name"] if enrollment_row else None,
            enrolled_at=enrollment_row["enrolled_at"] if enrollment_row else None,
            days_active=int(row["days_active"]),
            status=row["enrollment_status"],
        ),
        engagement=EngagementBlock(
            total_logins=row["total_logins"],
            unique_active_days=row["unique_active_days"],
            days_since_last_login=int(row["days_since_last_login"]),
            active_day_ratio=float(row["active_day_ratio"]),
            sunday_logins=row["sunday_logins"],
            late_night_logins=row["late_night_logins"],
        ),
        learning=LearningProgressBlock(
            lessons_started=row["lessons_started"],
            lessons_completed=row["lessons_completed"],
            lessons_abandoned=row["lessons_abandoned"],
            lesson_completion_rate=float(row["lesson_completion_rate"]),
            notes_downloaded=row["notes_downloaded"],
            sessions_attended=row["sessions_attended"],
            sessions_scheduled=row["sessions_scheduled"],
            attendance_rate=float(row["attendance_rate"]),
        ),
        assessments=AssessmentSummaryBlock(
            total_assessments=row["total_assessments"],
            avg_score_pct=float(row["avg_score_pct"]),
            best_score_pct=float(row["best_score_pct"]),
            worst_score_pct=float(row["worst_score_pct"]),
            recent_avg_score_pct=float(row["recent_avg_score_pct"]),
            failed_assessments=row["failed_assessments"],
            strong_assessments=row["strong_assessments"],
            score_volatility=float(row["score_volatility"]),
        ),
        recent_assessments=[
            RecentAssessment(
                title=r["title"],
                subject=r["subject"],
                chapter=r["chapter"],
                score=float(r["score"]),
                max_score=float(r["max_score"]),
                percentage=float(r["percentage"]),
                submitted_at=r["submitted_at"],
            )
            for r in recent_rows
        ],
    )


@router.get("/me/streak", response_model=StreakResponse)
def get_my_streak(
    payload: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Daily activity calendar + streak metrics from v_daily_engagement."""
    user_id = payload["sub"]

    rows = db.execute(text("""
        SELECT
            activity_date,
            logins,
            lessons_completed,
            quizzes_completed,
            total_events,
            (total_events > 0) AS was_active
        FROM v_daily_engagement
        WHERE student_user_id = :uid
        ORDER BY activity_date DESC
        LIMIT 90
    """), {"uid": user_id}).mappings().all()

    # Compute streaks (rows are DESC, so we walk in order)
    current_streak = 0
    longest_streak = 0
    running_streak = 0
    total_active = 0
    activity_list = []

    for r in rows:
        activity_list.append(DailyActivity(
            activity_date=r["activity_date"],
            logins=r["logins"],
            lessons_completed=r["lessons_completed"],
            quizzes_completed=r["quizzes_completed"],
            total_events=r["total_events"],
            was_active=r["was_active"],
        ))

    # Walk reverse-chronologically for current_streak
    for r in rows:
        if r["was_active"]:
            current_streak += 1
        else:
            break

    # Walk all for longest
    for r in reversed(rows):
        if r["was_active"]:
            running_streak += 1
            total_active += 1
            longest_streak = max(longest_streak, running_streak)
        else:
            running_streak = 0

    return StreakResponse(
        current_streak=current_streak,
        longest_streak=longest_streak,
        total_active_days=total_active,
        daily_activity=activity_list,
    )
# =============================================================
# PERSONALIZED RECOMMENDATIONS
# =============================================================
from app.schemas.course import (
    RecommendedLesson, RecommendationResponse, LessonSummary,
    WeakChapter, WeakChaptersResponse, TrackEventRequest, TrackEventResponse,
)
import uuid


@router.get("/me/recommended-lessons", response_model=RecommendationResponse)
def get_recommended_lessons(
    payload: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """
    Recommend next 5 lessons based on:
      - Student's weak subjects (priority)
      - Chapters where they've failed quizzes
      - Lessons they haven't completed yet
    """
    user_id = payload["sub"]

    # Get weak subjects from profile
    profile = db.execute(text("""
        SELECT weak_subjects FROM user_profiles WHERE user_id = :uid
    """), {"uid": user_id}).mappings().fetchone()

    weak_subjects = profile["weak_subjects"] if profile and profile["weak_subjects"] else []

    # Find lessons not yet completed in weak chapters
    weak_subject_lower = [s.lower() for s in weak_subjects]

    rows = db.execute(text("""
        WITH completed_lessons AS (
            SELECT (event_data->>'lesson_id') AS lesson_id
            FROM events
            WHERE user_id::text = :uid AND event_type = 'lesson_completed'
        ),
        weak_chapters AS (
            SELECT DISTINCT
                a.chapter,
                s.id AS subject_id
            FROM assessments a
            JOIN subjects s ON s.id = a.subject_id
            WHERE a.student_user_id::text = :uid
              AND (a.score::numeric / a.max_score) < 0.5
        )
        SELECT
            l.id::text,
            s.name AS subject_name,
            l.chapter,
            l.title,
            l.duration_minutes,
            l.difficulty_level,
            l.sequence_order,
            CASE
                WHEN EXISTS (SELECT 1 FROM weak_chapters wc
                             WHERE wc.chapter = l.chapter AND wc.subject_id = l.subject_id)
                    THEN 'You scored low on this chapter — revisit fundamentals'
                WHEN LOWER(s.name) = ANY(:weak_lower)
                    THEN 'Strengthen your weak subject'
                ELSE 'Continue your learning path'
            END AS reason
        FROM lessons l
        JOIN subjects s ON s.id = l.subject_id
        WHERE l.is_published = TRUE
          AND l.id::text NOT IN (SELECT lesson_id FROM completed_lessons WHERE lesson_id IS NOT NULL)
        ORDER BY
            CASE WHEN LOWER(s.name) = ANY(:weak_lower) THEN 0 ELSE 1 END,
            l.difficulty_level,
            l.sequence_order
        LIMIT 5
    """), {"uid": user_id, "weak_lower": weak_subject_lower}).mappings().all()

    return RecommendationResponse(
        student_user_id=user_id,
        recommendations=[
            RecommendedLesson(
                lesson=LessonSummary(
                    id=r["id"],
                    subject_name=r["subject_name"],
                    chapter=r["chapter"],
                    title=r["title"],
                    duration_minutes=r["duration_minutes"],
                    difficulty_level=r["difficulty_level"],
                    sequence_order=r["sequence_order"],
                ),
                reason=r["reason"],
            )
            for r in rows
        ],
    )


@router.get("/me/weak-chapters", response_model=WeakChaptersResponse)
def get_my_weak_chapters(
    payload: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Chapters where this student is underperforming."""
    user_id = payload["sub"]

    rows = db.execute(text("""
        SELECT
            s.name AS subject_name,
            a.chapter,
            COUNT(*) AS quizzes_attempted,
            ROUND(AVG((a.score::numeric / a.max_score) * 100), 2) AS avg_score,
            MAX(a.submitted_at) AS last_attempted_at
        FROM assessments a
        JOIN subjects s ON s.id = a.subject_id
        WHERE a.student_user_id::text = :uid
        GROUP BY s.name, a.chapter
        HAVING AVG((a.score::numeric / a.max_score) * 100) < 50
        ORDER BY avg_score ASC
        LIMIT 10
    """), {"uid": user_id}).mappings().all()

    return WeakChaptersResponse(
        student_user_id=user_id,
        weak_chapters=[
            WeakChapter(
                subject_name=r["subject_name"],
                chapter=r["chapter"],
                quizzes_attempted=r["quizzes_attempted"],
                avg_score=float(r["avg_score"]),
                last_attempted_at=r["last_attempted_at"],
            )
            for r in rows
        ],
    )


@router.post("/me/lessons/{lesson_id}/track-event", response_model=TrackEventResponse)
def track_lesson_event(
    lesson_id: str,
    body: TrackEventRequest,
    payload: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """
    Track a lesson event (frontend calls this on play, pause, complete, etc.)
    Writes one row to the events table.
    """
    from psycopg2.extras import Json
    user_id = payload["sub"]
    event_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    # Validate event type
    valid_events = {
        "lesson_started", "lesson_completed", "lesson_paused",
        "lesson_resumed", "lesson_abandoned", "lesson_replayed",
        "notes_downloaded", "playback_speed_changed",
    }
    if body.event_type not in valid_events:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type. Allowed: {sorted(valid_events)}",
        )

    # Build event_data with lesson_id always included
    event_data = dict(body.event_data) if body.event_data else {}
    event_data["lesson_id"] = lesson_id

    # Insert using SQLAlchemy's native JSON support (cleaner than string cast)
    import json as _json
    try:
        db.execute(text("""
            INSERT INTO events (
                id, user_id, event_type, event_data, session_id,
                ip_address, user_agent, created_at
            )
            VALUES (
                :id, :uid, :etype, CAST(:edata AS jsonb), :sid,
                NULL, NULL, NOW()
            )
        """), {
            "id": event_id,
            "uid": user_id,
            "etype": body.event_type,
            "edata": _json.dumps(event_data),
            "sid": session_id,
        })
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record event: {str(e)[:200]}",
        )

    return TrackEventResponse(event_id=event_id, accepted=True)