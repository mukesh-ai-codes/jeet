"""
JEET Simulator — Student State Machine

Each student carries a daily 'state' that evolves based on their actions:
  - engagement_score (0-100): platform activity level
  - confidence_score (0-100): self-belief from quiz/assessment results
  - burnout_score (0-100): fatigue accumulation
  - momentum (-1.0 to +1.0): trending direction over last 7 days
  - days_since_last_login: streak/gap tracking
  - days_since_good_quiz: emotional recency anchor

The state evolves daily based on:
  - what they did yesterday
  - their archetype's resilience
  - external calendar shocks
  - random life noise

This state is what makes simulated behavior FEEL real.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class StudentState:
    """Live mutable state for one student across the simulation."""

    student_id: str
    archetype_name: str

    # Core psychological scores (0-100)
    engagement_score: float = 70.0
    confidence_score: float = 65.0
    burnout_score: float = 20.0

    # Behavioral trackers
    momentum: float = 0.0  # -1 (declining) to +1 (improving)
    consecutive_active_days: int = 0
    consecutive_inactive_days: int = 0
    days_since_last_login: int = 0
    days_since_good_quiz: int = 0  # last quiz >= 60%
    days_since_bad_quiz: int = 999

    # Counters
    total_logins: int = 0
    total_lessons_completed: int = 0
    total_quizzes_attempted: int = 0
    total_quizzes_failed: int = 0  # <40%
    total_doubts_asked: int = 0
    total_late_night_sessions: int = 0
    total_mentor_interactions: int = 0

    # Financial signals
    payments_made: int = 0
    payments_failed: int = 0
    days_since_last_payment_event: int = 999

    # Outcome (set at end of simulation)
    final_status: str = "active"  # active | churned_academic | churned_financial | paused
    churn_day: Optional[int] = None
    churn_reason: Optional[str] = None

    # Cumulative engagement over time (for survival analysis)
    engagement_history: list = field(default_factory=list)


def initialize_state_from_archetype(student_id: str, archetype) -> StudentState:
    """
    Create initial state seeded by archetype baselines.
    Each archetype starts in a different psychological position.
    """
    s = StudentState(
        student_id=student_id,
        archetype_name=archetype.name,
    )

    # Engagement starts near archetype's natural level
    if archetype.name == "disciplined_topper":
        s.engagement_score = 88.0
        s.confidence_score = 80.0
        s.burnout_score = 12.0
    elif archetype.name == "diligent_struggler":
        s.engagement_score = 78.0
        s.confidence_score = 50.0
        s.burnout_score = 25.0
    elif archetype.name == "unengaged_genius":
        s.engagement_score = 55.0
        s.confidence_score = 75.0
        s.burnout_score = 15.0
    elif archetype.name == "hostel_burnout":
        s.engagement_score = 82.0   # Starts high — collapses later
        s.confidence_score = 70.0
        s.burnout_score = 22.0
    elif archetype.name == "parent_forced":
        s.engagement_score = 45.0
        s.confidence_score = 35.0
        s.burnout_score = 30.0
    elif archetype.name == "financially_stressed":
        s.engagement_score = 72.0
        s.confidence_score = 60.0
        s.burnout_score = 28.0
    elif archetype.name == "distracted_multitasker":
        s.engagement_score = 60.0
        s.confidence_score = 55.0
        s.burnout_score = 18.0
    elif archetype.name == "repeater":
        s.engagement_score = 80.0
        s.confidence_score = 55.0   # Lower from past failure
        s.burnout_score = 30.0      # Higher anxiety
    else:
        # Default safe defaults
        s.engagement_score = 65.0

    return s


# =============================================================
# DAILY STATE EVOLUTION
# =============================================================

def evolve_state_after_active_day(
    state: StudentState,
    archetype,
    session_duration_min: float,
    lessons_completed: int,
    quiz_attempted: bool,
    quiz_score: Optional[float],  # 0-100 if quiz_attempted else None
    late_night: bool,
    calendar_multiplier: float,
):
    """Update state after a day where the student was active."""

    # Engagement: rises with activity, weighted by session quality
    activity_lift = min(8, (session_duration_min / 60) * 3 + lessons_completed * 1.5)
    state.engagement_score = min(99.9, state.engagement_score + activity_lift)

    # Confidence shifts based on quiz performance
    if quiz_attempted and quiz_score is not None:
        if quiz_score >= 75:
            state.confidence_score = min(99.9, state.confidence_score + 5)
            state.days_since_good_quiz = 0
            state.days_since_bad_quiz += 1
        elif quiz_score >= 50:
            state.confidence_score = min(99.9, state.confidence_score + 1)
            state.days_since_good_quiz += 1
            state.days_since_bad_quiz += 1
        else:
            # Bad quiz — confidence drops, can cascade
            state.confidence_score = max(5, state.confidence_score - 8)
            state.total_quizzes_failed += 1
            state.days_since_good_quiz += 1
            state.days_since_bad_quiz = 0
        state.total_quizzes_attempted += 1

    # Burnout accumulates with late nights and high engagement
    if late_night:
        state.total_late_night_sessions += 1
        state.burnout_score = min(99.9, state.burnout_score + 3)
    else:
        # Burnout slowly recovers during normal-hour sessions
        state.burnout_score = max(0, state.burnout_score - 0.5)

    # Streak tracking
    state.consecutive_active_days += 1
    state.consecutive_inactive_days = 0
    state.days_since_last_login = 0
    state.days_since_good_quiz += 0 if quiz_attempted else 1
    state.days_since_bad_quiz += 0 if quiz_attempted else 1

    # Counters
    state.total_logins += 1
    state.total_lessons_completed += lessons_completed

    # Momentum update (exponential moving average)
    daily_signal = 0.0
    if quiz_attempted and quiz_score is not None:
        daily_signal = (quiz_score - 50) / 100  # -0.5 to +0.5
    daily_signal += (lessons_completed * 0.1) - 0.1
    state.momentum = 0.7 * state.momentum + 0.3 * daily_signal
    state.momentum = max(-1.0, min(1.0, state.momentum))


def evolve_state_after_inactive_day(state: StudentState, archetype):
    """Update state after a day where student did NOT log in."""

    # Engagement decays — speed depends on archetype
    decay = archetype.attendance_decay_per_week / 7 * 100 + 0.8
    state.engagement_score = max(0, state.engagement_score - decay)

    # Burnout slowly recovers when not engaging
    state.burnout_score = max(0, state.burnout_score - 1.2)

    # Streaks
    state.consecutive_inactive_days += 1
    state.consecutive_active_days = 0
    state.days_since_last_login += 1
    state.days_since_good_quiz += 1
    state.days_since_bad_quiz += 1

    # Momentum drifts negative
    state.momentum = max(-1.0, 0.85 * state.momentum - 0.05)


def apply_payment_failure_shock(state: StudentState):
    """Payment failure → engagement drop for the next week."""
    state.engagement_score = max(0, state.engagement_score - 12)
    state.confidence_score = max(0, state.confidence_score - 3)
    state.payments_failed += 1
    state.days_since_last_payment_event = 0


def apply_mentor_intervention_boost(state: StudentState):
    """A mentor call/intervention temporarily boosts engagement & confidence."""
    state.engagement_score = min(99.9, state.engagement_score + 15)
    state.confidence_score = min(99.9, state.confidence_score + 8)
    state.burnout_score = max(0, state.burnout_score - 10)
    state.total_mentor_interactions += 1
    state.momentum = min(1.0, state.momentum + 0.25)


# =============================================================
# CHURN RESOLUTION
# =============================================================

def evaluate_churn_risk(state: StudentState, day_index: int) -> Optional[str]:
    """
    Check if student should be marked as churned today.
    Returns churn reason or None.

    Thresholds tuned to match Indian EdTech reality:
    - ~20-25% academic churn (the biggest cause)
    - ~10-12% financial churn (parent-driven)
    - ~5-8% burnout pause (recovery possible)
    """

    # Strong academic disengagement (loosened threshold)
    if state.engagement_score < 18 and state.consecutive_inactive_days >= 10:
        return "academic_disengagement"

    # Burnout collapse → leads to PAUSE (recoverable), not full churn
    if state.burnout_score > 78 and state.engagement_score < 40:
        return "burnout"

    # Confidence collapse → academic churn cascade
    if state.confidence_score < 20 and state.total_quizzes_failed >= 3:
        return "confidence_collapse"

    # Long ghosting (reduced threshold)
    if state.consecutive_inactive_days >= 20:
        return "ghosted"

    return None


def apply_financial_churn_check(
    state: StudentState,
    archetype,
    rng,
    day_index: int,
) -> bool:
    """
    Separate financial churn check — triggered by archetype + probability.

    Real-world: financial churn is parent-driven, often unrelated to
    student engagement. Happens around payment cycles.
    """
    if state.final_status != "active":
        return False

    # Financial archetypes more prone to churn
    if archetype.name == "financially_stressed":
        # 0.15% daily probability after day 60 (post first EMI cycle)
        if day_index > 60 and rng.random() < 0.0015:
            return True
    elif archetype.name == "parent_forced":
        # Parents may stop paying when student shows no improvement
        if day_index > 45 and state.confidence_score < 35 and rng.random() < 0.0010:
            return True
    elif archetype.name == "unengaged_genius":
        # May not renew — early signal at end of first quarter
        if day_index > 80 and state.engagement_score < 40 and rng.random() < 0.0008:
            return True
    else:
        # Generic financial risk: very low base rate
        if day_index > 50 and rng.random() < 0.0003:
            return True

    return False