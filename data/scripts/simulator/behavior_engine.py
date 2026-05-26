"""
JEET Simulator — Daily Behavior Decision Engine

For each student each day, decides:
  - Will they log in?
  - For how long?
  - Will they take a quiz?
  - Will they ask a doubt?
  - Will they have a late-night session?
  - Should mentor intervene?

All decisions are probabilistic but archetype + state + calendar driven.
"""

import random
from datetime import date
from typing import Optional, Tuple

from simulator.calendar_effects import composite_calendar_multiplier
from simulator.student_state import StudentState


def decide_will_login_today(
    rng: random.Random,
    state: StudentState,
    archetype,
    day: date,
    grade: int,
    target_exam: str,
    target_exam_date: date,
) -> bool:
    """Decide if this student logs in on this day."""

    # Base probability from archetype
    base_p = archetype.daily_login_probability

    # Adjust for current engagement state
    engagement_modifier = (state.engagement_score / 70.0)  # 0.0 to ~1.4
    engagement_modifier = max(0.3, min(1.4, engagement_modifier))

    # Calendar effect (holidays, weekends, exam proximity)
    cal_modifier = composite_calendar_multiplier(
        day, archetype.name, grade, target_exam, target_exam_date,
    )

    # Burnout suppression — high burnout → lower login probability
    burnout_modifier = 1.0 - (state.burnout_score / 200.0)  # 0.5 to 1.0

    # Confidence effect — very low confidence reduces login
    if state.confidence_score < 25:
        confidence_modifier = 0.6
    elif state.confidence_score < 40:
        confidence_modifier = 0.85
    else:
        confidence_modifier = 1.0

    # Post-failed-quiz blues: recent bad quiz reduces login for 3-5 days
    if state.days_since_bad_quiz <= 3 and state.confidence_score < 50:
        confidence_modifier *= 0.7

    # Consecutive inactive penalty (decay, not snap-back)
    if state.consecutive_inactive_days >= 7:
        confidence_modifier *= 0.6
    elif state.consecutive_inactive_days >= 14:
        confidence_modifier *= 0.4

    p = base_p * engagement_modifier * cal_modifier * burnout_modifier * confidence_modifier

    # Random life noise
    p *= rng.uniform(0.85, 1.15)

    return rng.random() < min(0.98, p)


def decide_session_duration(
    rng: random.Random, state: StudentState, archetype,
) -> float:
    """Returns session duration in minutes for an active day."""

    base_mean = archetype.avg_session_minutes
    base_std = archetype.session_minutes_std

    # State modifier
    engagement_factor = state.engagement_score / 70.0
    burnout_factor = max(0.5, 1.0 - state.burnout_score / 150.0)

    mean = base_mean * engagement_factor * burnout_factor
    duration = rng.gauss(mean, base_std)

    return max(5, min(240, duration))


def decide_is_late_night(
    rng: random.Random, state: StudentState, archetype,
) -> bool:
    """Will this session happen between 11pm-2am?"""
    base_p = archetype.late_night_usage_probability

    # Burnout increases late night probability (insomnia, anxiety)
    if state.burnout_score > 60:
        base_p *= 1.4

    return rng.random() < min(0.85, base_p)


def decide_lessons_completed(
    rng: random.Random, state: StudentState, archetype, session_minutes: float,
) -> int:
    """How many lessons completed during this session."""
    # Each lesson ~ 45min average
    capacity = max(0, int(session_minutes / 45))
    if capacity == 0:
        return 0

    # Quality factor based on archetype + state
    quality = (state.engagement_score / 100.0) * (1.0 - state.burnout_score / 200.0)
    expected = capacity * quality

    return max(0, int(round(rng.gauss(expected, 0.5))))


def decide_quiz_attempted(
    rng: random.Random, state: StudentState, archetype, day_index: int,
) -> bool:
    """Quizzes happen ~every 4-7 days for engaged students."""

    # Cadence: more engaged students take quizzes more often
    base_cadence_days = 7
    if state.engagement_score > 75:
        base_cadence_days = 4
    elif state.engagement_score > 50:
        base_cadence_days = 6

    # Sundays = mock test day
    if day_index % 7 == 6:
        base_cadence_days = max(3, base_cadence_days - 2)

    p_quiz = 1.0 / base_cadence_days
    p_quiz *= archetype.mock_test_completion_rate

    return rng.random() < p_quiz


def decide_quiz_score(
    rng: random.Random, state: StudentState, archetype,
) -> float:
    """Returns quiz score 0-100."""
    base_mean = archetype.quiz_score_mean
    base_std = archetype.quiz_score_std

    # Momentum & confidence shift performance
    confidence_shift = (state.confidence_score - 65) * 0.15
    momentum_shift = state.momentum * 5
    burnout_penalty = state.burnout_score * 0.10

    mean = base_mean + confidence_shift + momentum_shift - burnout_penalty
    score = rng.gauss(mean, base_std)
    return max(5, min(100, score))


def decide_doubt_asked(
    rng: random.Random, state: StudentState, archetype, session_minutes: float,
) -> int:
    """How many doubts does the student ask in this session?"""
    base_freq = archetype.doubt_asking_frequency

    # Low-confidence students with active engagement ask MORE
    if state.confidence_score < 50 and state.engagement_score > 50:
        base_freq *= 1.5

    # Very-low engagement = silent (don't bother asking)
    if state.engagement_score < 30:
        base_freq *= 0.4

    expected = base_freq * (session_minutes / 60.0)
    return max(0, int(round(rng.gauss(expected, 0.8))))


def decide_mentor_intervention(
    rng: random.Random, state: StudentState, archetype, day_index: int,
) -> bool:
    """
    Should a mentor intervention happen today?
    Triggered by behavior patterns AND archetype's acceptance rate.
    """
    # Trigger conditions
    needs_intervention = False
    if state.consecutive_inactive_days >= 5:
        needs_intervention = True
    elif state.engagement_score < 35:
        needs_intervention = True
    elif state.total_quizzes_failed >= 3 and state.confidence_score < 40:
        needs_intervention = True
    elif state.burnout_score > 75:
        needs_intervention = True

    if not needs_intervention:
        return False

    # Probability gated by archetype acceptance + recency
    if state.total_mentor_interactions > 0 and day_index < 30:
        return False  # No spam

    p = archetype.mentor_call_acceptance_rate * 0.25  # Daily probability cap
    return rng.random() < p