"""
JEET Simulator — Event Factory

Given a student's daily decisions, generates realistic event records
ready for bulk insertion into the events / attendance / assessments tables.

This is the source of the ~1.4M event stream that powers ML training.
"""

import random
import uuid
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Tuple


# =============================================================
# EVENT TYPE TAXONOMY (the 45 events from our Day 3 brief)
# =============================================================

# Categorized for clarity
EVENT_AUTH = ["user_login", "user_logout", "session_timeout", "device_switched"]
EVENT_CONTENT = [
    "lesson_started", "lesson_paused", "lesson_resumed", "lesson_completed",
    "lesson_abandoned", "lesson_replayed", "playback_speed_changed",
    "notes_downloaded", "video_quality_changed",
]
EVENT_ASSESSMENT = [
    "quiz_started", "quiz_submitted", "quiz_abandoned",
    "mock_test_started", "mock_test_submitted", "mock_test_abandoned",
    "score_revealed", "solution_viewed",
]
EVENT_DOUBT = [
    "doubt_asked_tutor", "doubt_asked_mentor", "doubt_resolved",
    "doubt_upvoted",
]
EVENT_INTERVENTION = [
    "nudge_received", "nudge_clicked", "nudge_dismissed",
    "mentor_call_scheduled", "mentor_call_attended", "mentor_call_missed",
]
EVENT_BUSINESS = ["plan_viewed", "payment_initiated", "payment_succeeded", "payment_failed"]
EVENT_PARENT = ["parent_dashboard_opened", "parent_report_viewed", "parent_whatsapp_clicked"]


# =============================================================
# DEVICE / SESSION HELPERS
# =============================================================
DEVICES = ["mobile_android", "mobile_ios", "web_chrome", "web_safari", "tablet_android"]
DEVICE_WEIGHTS = [0.55, 0.10, 0.20, 0.08, 0.07]  # Indian mobile-first reality


def _pick_device(rng):
    return rng.choices(DEVICES, weights=DEVICE_WEIGHTS, k=1)[0]


def _session_login_time(rng, day: date, is_late_night: bool) -> datetime:
    """Pick a realistic login timestamp for the day."""
    if is_late_night:
        # 11pm - 2am window
        if rng.random() < 0.6:
            hour = rng.choice([23, 0, 1])
        else:
            hour = rng.choice([22, 2])
        if hour == 23 or hour == 22:
            return datetime.combine(day, time(hour, rng.randint(0, 59)))
        else:
            # 0, 1, 2 am happen NEXT day
            return datetime.combine(day + timedelta(days=1), time(hour, rng.randint(0, 59)))

    # Normal hours — bimodal: morning peak (6-9am) and evening peak (6-10pm)
    if rng.random() < 0.35:
        hour = rng.choices([6, 7, 8, 9], weights=[0.15, 0.30, 0.30, 0.25])[0]
    else:
        hour = rng.choices([15, 16, 17, 18, 19, 20, 21],
                          weights=[0.05, 0.10, 0.15, 0.20, 0.20, 0.20, 0.10])[0]

    return datetime.combine(day, time(hour, rng.randint(0, 59), rng.randint(0, 59)))


# =============================================================
# CORE EVENT BUILDERS
# =============================================================

def _build_event(
    user_id: str,
    event_type: str,
    event_data: dict,
    session_id: str,
    timestamp: datetime,
    device: str,
) -> dict:
    """Construct one event record matching the events table schema."""
    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_type": event_type,
        "event_data": event_data,
        "session_id": session_id,
        "ip_address": None,  # Synthetic, leave NULL
        "user_agent": device,
        "created_at": timestamp,
    }


def generate_daily_events(
    rng: random.Random,
    student_user_id: str,
    day: date,
    session_minutes: float,
    lessons_completed: int,
    quiz_attempted: bool,
    quiz_score: Optional[float],
    doubts_asked: int,
    is_late_night: bool,
    available_lesson_ids: list,
    available_subject_ids: dict,  # subject_slug -> id
    weak_subjects: list,
) -> List[dict]:
    """
    Generate all events for one active day of one student.

    Returns a list of event dicts ready for bulk insertion.
    """
    events = []
    session_id = str(uuid.uuid4())
    device = _pick_device(rng)

    login_at = _session_login_time(rng, day, is_late_night)
    current_time = login_at

    # ---------------- LOGIN ----------------
    events.append(_build_event(
        student_user_id, "user_login",
        {
            "device": device,
            "is_late_night": is_late_night,
            "session_duration_target_min": round(session_minutes, 1),
        },
        session_id, current_time, device,
    ))

    # ---------------- LESSONS ----------------
    # Allocate session time: lessons get ~70%, quiz ~20%, doubts ~10%
    lesson_time_budget = session_minutes * 0.70
    time_per_lesson = lesson_time_budget / max(1, lessons_completed + 1)

    # How many lessons did they START (vs complete)?
    # Some students start a lesson but abandon
    lessons_started = lessons_completed + (1 if rng.random() < 0.30 else 0)
    lessons_started = min(lessons_started, len(available_lesson_ids))

    chosen_lessons = rng.sample(available_lesson_ids, lessons_started) if lessons_started > 0 else []

    for idx, lesson_id in enumerate(chosen_lessons):
        # lesson_started
        current_time += timedelta(seconds=rng.randint(15, 90))
        events.append(_build_event(
            student_user_id, "lesson_started",
            {"lesson_id": lesson_id, "watch_speed": rng.choice([1.0, 1.0, 1.25, 1.5, 2.0])},
            session_id, current_time, device,
        ))

        # Did they abandon or complete?
        is_completed = idx < lessons_completed

        if is_completed:
            # Pause maybe
            if rng.random() < 0.40:
                current_time += timedelta(minutes=rng.randint(5, 15))
                events.append(_build_event(
                    student_user_id, "lesson_paused",
                    {"lesson_id": lesson_id, "watch_pct": rng.randint(30, 70)},
                    session_id, current_time, device,
                ))
                # Resume
                current_time += timedelta(seconds=rng.randint(30, 600))
                events.append(_build_event(
                    student_user_id, "lesson_resumed",
                    {"lesson_id": lesson_id},
                    session_id, current_time, device,
                ))

            # Speed change is common
            if rng.random() < 0.25:
                current_time += timedelta(minutes=rng.randint(2, 8))
                events.append(_build_event(
                    student_user_id, "playback_speed_changed",
                    {"lesson_id": lesson_id, "new_speed": rng.choice([1.25, 1.5, 2.0])},
                    session_id, current_time, device,
                ))

            # Replay confusing segment (more common for weak subjects)
            replay_p = 0.20
            events.append(_build_event(
                student_user_id, "lesson_replayed",
                {"lesson_id": lesson_id, "segment_start_sec": rng.randint(60, 1500)},
                session_id, current_time + timedelta(minutes=rng.randint(3, 10)), device,
            )) if rng.random() < replay_p else None

            # Complete
            current_time += timedelta(minutes=int(time_per_lesson * rng.uniform(0.7, 1.1)))
            events.append(_build_event(
                student_user_id, "lesson_completed",
                {
                    "lesson_id": lesson_id,
                    "completion_pct": rng.randint(85, 100),
                    "duration_watched_min": round(time_per_lesson * rng.uniform(0.7, 1.1), 1),
                },
                session_id, current_time, device,
            ))

            # Notes download (some students)
            if rng.random() < 0.18:
                events.append(_build_event(
                    student_user_id, "notes_downloaded",
                    {"lesson_id": lesson_id},
                    session_id, current_time + timedelta(seconds=rng.randint(5, 60)), device,
                ))
        else:
            # Abandoned
            current_time += timedelta(minutes=rng.randint(3, 15))
            events.append(_build_event(
                student_user_id, "lesson_abandoned",
                {
                    "lesson_id": lesson_id,
                    "watch_pct_at_exit": rng.randint(10, 45),
                    "exit_reason": rng.choice(["distracted", "confused", "tired", "interrupted"]),
                },
                session_id, current_time, device,
            ))

    # ---------------- QUIZ / ASSESSMENT ----------------
    if quiz_attempted and quiz_score is not None:
        # Pick a subject (bias toward weak subjects for diligent_struggler etc.)
        subjects_for_quiz = list(available_subject_ids.keys())
        if weak_subjects and rng.random() < 0.55:
            weak_overlap = [s for s in weak_subjects if s.lower() in subjects_for_quiz]
            if weak_overlap:
                subject_slug = rng.choice([s.lower() for s in weak_overlap if s.lower() in available_subject_ids])
            else:
                subject_slug = rng.choice(subjects_for_quiz)
        else:
            subject_slug = rng.choice(subjects_for_quiz)

        current_time += timedelta(minutes=rng.randint(5, 15))
        is_mock_test = (day.weekday() == 6 and rng.random() < 0.4)  # Sunday mock
        quiz_kind_start = "mock_test_started" if is_mock_test else "quiz_started"
        quiz_kind_end = "mock_test_submitted" if is_mock_test else "quiz_submitted"

        events.append(_build_event(
            student_user_id, quiz_kind_start,
            {"subject": subject_slug, "num_questions": 10 if not is_mock_test else 30},
            session_id, current_time, device,
        ))

        # Quiz duration
        quiz_duration = rng.randint(15, 60) if is_mock_test else rng.randint(8, 25)
        current_time += timedelta(minutes=quiz_duration)

        # 10% chance student abandons quiz (low engagement signal)
        if rng.random() < 0.10 and quiz_score < 50:
            abandon_kind = "mock_test_abandoned" if is_mock_test else "quiz_abandoned"
            events.append(_build_event(
                student_user_id, abandon_kind,
                {"subject": subject_slug, "questions_answered": rng.randint(2, 6)},
                session_id, current_time, device,
            ))
        else:
            events.append(_build_event(
                student_user_id, quiz_kind_end,
                {
                    "subject": subject_slug,
                    "score_percentage": round(quiz_score, 1),
                    "time_taken_min": quiz_duration,
                },
                session_id, current_time, device,
            ))

            # Score reveal
            current_time += timedelta(seconds=rng.randint(5, 30))
            events.append(_build_event(
                student_user_id, "score_revealed",
                {"subject": subject_slug, "score": round(quiz_score, 1)},
                session_id, current_time, device,
            ))

            # Low score → view solution
            if quiz_score < 65 and rng.random() < 0.65:
                events.append(_build_event(
                    student_user_id, "solution_viewed",
                    {"subject": subject_slug},
                    session_id, current_time + timedelta(seconds=rng.randint(30, 180)), device,
                ))

    # ---------------- DOUBTS ----------------
    for i in range(doubts_asked):
        current_time += timedelta(minutes=rng.randint(3, 12))
        doubt_kind = "doubt_asked_tutor" if rng.random() < 0.85 else "doubt_asked_mentor"

        # Doubt subject biased toward weak subjects
        if weak_subjects and rng.random() < 0.60:
            doubt_subject = rng.choice(weak_subjects).lower()
        else:
            doubt_subject = rng.choice(list(available_subject_ids.keys()))

        events.append(_build_event(
            student_user_id, doubt_kind,
            {
                "subject": doubt_subject,
                "question_length_chars": rng.randint(20, 280),
                "tutor_response_time_ms": rng.randint(800, 3500),
            },
            session_id, current_time, device,
        ))

        # Resolution (most doubts get resolved)
        if rng.random() < 0.88:
            events.append(_build_event(
                student_user_id, "doubt_resolved",
                {"subject": doubt_subject, "helpful": rng.random() < 0.78},
                session_id, current_time + timedelta(seconds=rng.randint(30, 240)), device,
            ))

    # ---------------- LOGOUT ----------------
    current_time = max(current_time, login_at + timedelta(minutes=int(session_minutes)))
    events.append(_build_event(
        student_user_id, "user_logout",
        {"session_duration_min": round((current_time - login_at).total_seconds() / 60, 1)},
        session_id, current_time, device,
    ))

    return events


# =============================================================
# ATTENDANCE RECORD GENERATION
# =============================================================
def generate_attendance_record(
    rng: random.Random,
    enrollment_id: str,
    lesson_id: str,
    subject_id: str,
    session_date: date,
    joined: bool,
    engagement_score: float,
    archetype_name: str,
) -> dict:
    """Generate one attendance row for a live session."""
    if joined:
        joined_at = datetime.combine(session_date, time(rng.randint(16, 20), rng.randint(0, 59)))
        # Duration depends on engagement
        if engagement_score > 70:
            duration = rng.randint(50, 90)
        elif engagement_score > 40:
            duration = rng.randint(25, 60)
        else:
            duration = rng.randint(10, 35)
        left_at = joined_at + timedelta(minutes=duration)
        # Cap strictly below 100 to fit NUMERIC(4,2) schema (max 99.99)
        eng_score_session = max(0, min(99.9, engagement_score + rng.gauss(0, 8)))
    else:
        joined_at = None
        left_at = None
        duration = 0
        eng_score_session = None

    return {
        "id": str(uuid.uuid4()),
        "enrollment_id": enrollment_id,
        "lesson_id": lesson_id,
        "subject_id": subject_id,
        "session_date": session_date,
        "joined": joined,
        "joined_at": joined_at,
        "left_at": left_at,
        "duration_minutes": duration,
        "engagement_score": round(eng_score_session, 2) if eng_score_session else None,
        "created_at": datetime.combine(session_date, time(20, 0)),
    }


# =============================================================
# ASSESSMENT RECORD GENERATION
# =============================================================
def generate_assessment_record(
    rng: random.Random,
    student_user_id: str,
    subject_id: str,
    subject_slug: str,
    quiz_score: float,
    submitted_at: datetime,
    is_mock: bool = False,
) -> dict:
    """Generate one assessment record from a quiz event."""

    if is_mock:
        max_score = 300  # Full mock test out of 300 (JEE/NEET pattern)
        title = f"Mock Test — {subject_slug.title()}"
        difficulty = rng.randint(3, 5)
        time_min = rng.randint(60, 180)
    else:
        max_score = 100
        title = f"{subject_slug.title()} Quiz - Chapter Test"
        difficulty = rng.randint(2, 4)
        time_min = rng.randint(15, 45)

    score = (quiz_score / 100.0) * max_score

    chapters_pool = {
        "physics": ["Mechanics", "Thermodynamics", "Electrostatics", "Magnetism",
                    "Optics", "Modern Physics", "Waves", "Current Electricity"],
        "chemistry": ["Organic Chemistry", "Physical Chemistry", "Inorganic Chemistry",
                      "Coordination Compounds", "Equilibrium", "Thermodynamics"],
        "mathematics": ["Algebra", "Calculus", "Coordinate Geometry", "Trigonometry",
                        "Probability", "Vectors", "Matrices"],
        "biology": ["Cell Biology", "Genetics", "Human Physiology", "Plant Physiology",
                    "Ecology", "Reproduction", "Evolution"],
    }
    chapter = rng.choice(chapters_pool.get(subject_slug, ["General"]))

    return {
        "id": str(uuid.uuid4()),
        "student_user_id": student_user_id,
        "subject_id": subject_id,
        "chapter": chapter,
        "title": title,
        "score": round(score, 2),
        "max_score": max_score,
        "time_taken_minutes": time_min,
        "difficulty_level": difficulty,
        "submitted_at": submitted_at,
    }