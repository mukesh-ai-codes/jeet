"""
JEET Simulator — Student Archetype Engine

Each student is assigned one of 8 archetypes that drives their entire
120-day behavior. The archetype determines:
  - daily login probability
  - attendance baseline
  - quiz score distribution
  - churn risk
  - intervention responsiveness
  - parent involvement level

This is what makes ML predictions learnable rather than random.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ArchetypeProfile:
    """
    Parameters defining a student archetype's behavior.

    All values are baselines — the simulator will add daily noise + drift.
    """
    name: str
    description: str

    # ---------- Engagement Baseline ----------
    daily_login_probability: float       # 0.0 - 1.0
    avg_session_minutes: float           # mean session duration
    session_minutes_std: float           # standard deviation
    daily_study_hours_mean: float
    daily_study_hours_std: float

    # ---------- Attendance ----------
    attendance_rate: float               # 0.0 - 1.0 (live sessions joined)
    attendance_decay_per_week: float     # how fast attendance drops weekly

    # ---------- Academic Performance ----------
    quiz_score_mean: float               # 0-100
    quiz_score_std: float
    assignment_completion_rate: float

    # ---------- Behavioral Signals ----------
    doubt_asking_frequency: float        # doubts per active day
    weekend_engagement_multiplier: float # >1 means more engaged weekends
    late_night_usage_probability: float  # P(study between 11pm-2am)
    mock_test_completion_rate: float     # 0-1

    # ---------- Churn ----------
    base_churn_probability: float        # 90-day churn baseline
    churn_lag_days_mean: float           # how long disengagement lasts before churning

    # ---------- Intervention ----------
    intervention_response_rate: float    # P(positive response to nudges)
    mentor_call_acceptance_rate: float

    # ---------- Parent Dynamics ----------
    parent_dashboard_open_per_week: float
    parent_pressure_level: float         # 0-10
    parent_payment_punctuality: float    # 0-1 (1 = always on time)

    # ---------- Population Share ----------
    population_weight: float             # what % of students are this archetype


# =============================================================
# THE 8 ARCHETYPES
# =============================================================

DISCIPLINED_TOPPER = ArchetypeProfile(
    name="disciplined_topper",
    description="Top 5%. Consistent, high-performing, low-maintenance.",
    daily_login_probability=0.92,
    avg_session_minutes=85,
    session_minutes_std=15,
    daily_study_hours_mean=5.2,
    daily_study_hours_std=0.8,
    attendance_rate=0.95,
    attendance_decay_per_week=0.001,
    quiz_score_mean=82,
    quiz_score_std=6,
    assignment_completion_rate=0.97,
    doubt_asking_frequency=1.2,
    weekend_engagement_multiplier=1.1,
    late_night_usage_probability=0.15,
    mock_test_completion_rate=0.98,
    base_churn_probability=0.04,
    churn_lag_days_mean=45,
    intervention_response_rate=0.85,
    mentor_call_acceptance_rate=0.90,
    parent_dashboard_open_per_week=4.5,
    parent_pressure_level=5.5,
    parent_payment_punctuality=0.98,
    population_weight=0.08,
)

DILIGENT_STRUGGLER = ArchetypeProfile(
    name="diligent_struggler",
    description="High effort, low results. Attends everything, scores poorly.",
    daily_login_probability=0.85,
    avg_session_minutes=70,
    session_minutes_std=18,
    daily_study_hours_mean=4.0,
    daily_study_hours_std=1.0,
    attendance_rate=0.88,
    attendance_decay_per_week=0.008,  # Slowly demoralized
    quiz_score_mean=42,
    quiz_score_std=10,
    assignment_completion_rate=0.85,
    doubt_asking_frequency=3.5,  # Asks lots of basic doubts
    weekend_engagement_multiplier=1.0,
    late_night_usage_probability=0.25,
    mock_test_completion_rate=0.80,
    base_churn_probability=0.28,
    churn_lag_days_mean=60,
    intervention_response_rate=0.70,
    mentor_call_acceptance_rate=0.85,
    parent_dashboard_open_per_week=3.0,
    parent_pressure_level=6.0,
    parent_payment_punctuality=0.85,
    population_weight=0.15,
)

UNENGAGED_GENIUS = ArchetypeProfile(
    name="unengaged_genius",
    description="Self-taught from YouTube. Skips live sessions. High scores.",
    daily_login_probability=0.45,
    avg_session_minutes=110,  # When they log in, they go deep
    session_minutes_std=40,
    daily_study_hours_mean=3.5,  # But not consistent daily
    daily_study_hours_std=2.5,
    attendance_rate=0.35,
    attendance_decay_per_week=0.012,
    quiz_score_mean=78,
    quiz_score_std=12,
    assignment_completion_rate=0.60,
    doubt_asking_frequency=0.3,  # Rarely, but deep
    weekend_engagement_multiplier=1.4,  # Crams on weekends
    late_night_usage_probability=0.55,  # Night owl
    mock_test_completion_rate=0.85,
    base_churn_probability=0.42,
    churn_lag_days_mean=30,  # Quick to leave
    intervention_response_rate=0.40,  # Hard to reach
    mentor_call_acceptance_rate=0.50,
    parent_dashboard_open_per_week=1.5,
    parent_pressure_level=3.0,
    parent_payment_punctuality=0.85,  # Critical, may not renew
    population_weight=0.06,
)

HOSTEL_BURNOUT = ArchetypeProfile(
    name="hostel_burnout",
    description="Started strong in Kota/hostel. Engagement collapses by month 3.",
    daily_login_probability=0.75,  # Initially high, decays
    avg_session_minutes=65,
    session_minutes_std=25,
    daily_study_hours_mean=3.0,
    daily_study_hours_std=1.5,
    attendance_rate=0.78,
    attendance_decay_per_week=0.025,  # Steep decay
    quiz_score_mean=58,
    quiz_score_std=15,
    assignment_completion_rate=0.65,
    doubt_asking_frequency=1.0,  # Decreases over time
    weekend_engagement_multiplier=0.7,  # Burnt out on weekends
    late_night_usage_probability=0.65,  # Insomnia patterns
    mock_test_completion_rate=0.55,
    base_churn_probability=0.55,
    churn_lag_days_mean=25,
    intervention_response_rate=0.50,
    mentor_call_acceptance_rate=0.65,  # Needs the warmth
    parent_dashboard_open_per_week=2.0,
    parent_pressure_level=7.5,
    parent_payment_punctuality=0.92,
    population_weight=0.12,
)

PARENT_FORCED = ArchetypeProfile(
    name="parent_forced",
    description="Doesn't want JEE/NEET. Engagement is performative.",
    daily_login_probability=0.60,  # Performative — opens app when parent around
    avg_session_minutes=25,  # Short sessions
    session_minutes_std=10,
    daily_study_hours_mean=1.5,
    daily_study_hours_std=1.0,
    attendance_rate=0.50,
    attendance_decay_per_week=0.015,
    quiz_score_mean=32,
    quiz_score_std=12,
    assignment_completion_rate=0.40,
    doubt_asking_frequency=0.2,  # Doesn't care enough to ask
    weekend_engagement_multiplier=0.5,
    late_night_usage_probability=0.10,
    mock_test_completion_rate=0.30,
    base_churn_probability=0.68,
    churn_lag_days_mean=20,
    intervention_response_rate=0.25,  # Hard to motivate
    mentor_call_acceptance_rate=0.40,
    parent_dashboard_open_per_week=6.0,  # Helicopter parent
    parent_pressure_level=9.0,
    parent_payment_punctuality=0.95,
    population_weight=0.10,
)

FINANCIALLY_STRESSED = ArchetypeProfile(
    name="financially_stressed",
    description="High intent, inconsistent execution. EMI on coaching fees.",
    daily_login_probability=0.70,
    avg_session_minutes=80,  # Goes hard when they study
    session_minutes_std=30,
    daily_study_hours_mean=4.5,
    daily_study_hours_std=2.0,
    attendance_rate=0.75,
    attendance_decay_per_week=0.005,
    quiz_score_mean=64,
    quiz_score_std=14,
    assignment_completion_rate=0.78,
    doubt_asking_frequency=2.0,
    weekend_engagement_multiplier=1.5,  # Catches up weekends
    late_night_usage_probability=0.45,  # Studies after work/chores
    mock_test_completion_rate=0.75,
    base_churn_probability=0.38,
    churn_lag_days_mean=35,
    intervention_response_rate=0.75,  # Responsive — high emotional stakes
    mentor_call_acceptance_rate=0.80,
    parent_dashboard_open_per_week=2.5,
    parent_pressure_level=7.0,
    parent_payment_punctuality=0.55,  # Late payments common
    population_weight=0.14,
)

DISTRACTED_MULTITASKER = ArchetypeProfile(
    name="distracted_multitasker",
    description="Instagram, gaming, Netflix. Wants to crack JEE but can't focus.",
    daily_login_probability=0.55,
    avg_session_minutes=45,
    session_minutes_std=30,
    daily_study_hours_mean=2.5,
    daily_study_hours_std=2.0,  # High variance — bursty
    attendance_rate=0.62,
    attendance_decay_per_week=0.010,
    quiz_score_mean=52,
    quiz_score_std=18,
    assignment_completion_rate=0.55,
    doubt_asking_frequency=0.8,
    weekend_engagement_multiplier=0.7,  # Gaming weekends
    late_night_usage_probability=0.50,
    mock_test_completion_rate=0.50,
    base_churn_probability=0.35,
    churn_lag_days_mean=40,
    intervention_response_rate=0.55,
    mentor_call_acceptance_rate=0.60,
    parent_dashboard_open_per_week=3.5,
    parent_pressure_level=6.5,
    parent_payment_punctuality=0.88,
    population_weight=0.18,
)

REPEATER = ArchetypeProfile(
    name="repeater",
    description="Drop year. Failed last attempt. Anxiety + high commitment.",
    daily_login_probability=0.82,
    avg_session_minutes=95,
    session_minutes_std=25,
    daily_study_hours_mean=5.5,
    daily_study_hours_std=1.5,
    attendance_rate=0.85,
    attendance_decay_per_week=0.012,  # Anxiety spikes by exam
    quiz_score_mean=68,
    quiz_score_std=13,
    assignment_completion_rate=0.82,
    doubt_asking_frequency=2.5,
    weekend_engagement_multiplier=1.2,
    late_night_usage_probability=0.55,
    mock_test_completion_rate=0.88,
    base_churn_probability=0.22,
    churn_lag_days_mean=50,
    intervention_response_rate=0.78,
    mentor_call_acceptance_rate=0.85,
    parent_dashboard_open_per_week=2.0,
    parent_pressure_level=8.0,
    parent_payment_punctuality=0.92,
    population_weight=0.17,
)


# =============================================================
# REGISTRY
# =============================================================
ALL_ARCHETYPES: Dict[str, ArchetypeProfile] = {
    a.name: a for a in [
        DISCIPLINED_TOPPER,
        DILIGENT_STRUGGLER,
        UNENGAGED_GENIUS,
        HOSTEL_BURNOUT,
        PARENT_FORCED,
        FINANCIALLY_STRESSED,
        DISTRACTED_MULTITASKER,
        REPEATER,
    ]
}

# Sanity: weights sum to 1.0
_total = sum(a.population_weight for a in ALL_ARCHETYPES.values())
assert abs(_total - 1.0) < 0.001, f"Archetype weights sum to {_total}, must be 1.0"


def sample_archetype(rng) -> ArchetypeProfile:
    """Sample an archetype weighted by population share."""
    names = list(ALL_ARCHETYPES.keys())
    weights = [ALL_ARCHETYPES[n].population_weight for n in names]
    chosen = rng.choices(names, weights=weights, k=1)[0]
    return ALL_ARCHETYPES[chosen]


# =============================================================
# PARENT ARCHETYPES
# =============================================================
@dataclass(frozen=True)
class ParentArchetype:
    name: str
    description: str
    dashboard_opens_per_week: float
    whatsapp_response_rate: float
    payment_punctuality: float
    pressure_level: float        # affects student stress
    population_weight: float


HELICOPTER_MONITOR = ParentArchetype(
    name="helicopter_monitor",
    description="Daily check, texts mentor often",
    dashboard_opens_per_week=5.5,
    whatsapp_response_rate=0.95,
    payment_punctuality=0.98,
    pressure_level=8.0,
    population_weight=0.25,
)
HOPEFUL_INVESTOR = ParentArchetype(
    name="hopeful_investor",
    description="Weekly check, trusts the process",
    dashboard_opens_per_week=1.5,
    whatsapp_response_rate=0.70,
    payment_punctuality=0.85,
    pressure_level=5.0,
    population_weight=0.40,
)
HANDS_OFF_TRUSTEE = ParentArchetype(
    name="hands_off_trustee",
    description="Monthly check, last-minute renewals",
    dashboard_opens_per_week=0.4,
    whatsapp_response_rate=0.45,
    payment_punctuality=0.60,
    pressure_level=2.5,
    population_weight=0.20,
)
ANXIOUS_PRESSURIZER = ParentArchetype(
    name="anxious_pressurizer",
    description="Multiple daily checks, panic-calls mentor",
    dashboard_opens_per_week=12.0,
    whatsapp_response_rate=0.98,
    payment_punctuality=0.95,
    pressure_level=9.5,
    population_weight=0.15,
)

ALL_PARENT_ARCHETYPES: Dict[str, ParentArchetype] = {
    p.name: p for p in [
        HELICOPTER_MONITOR, HOPEFUL_INVESTOR, HANDS_OFF_TRUSTEE, ANXIOUS_PRESSURIZER,
    ]
}
_pt = sum(p.population_weight for p in ALL_PARENT_ARCHETYPES.values())
assert abs(_pt - 1.0) < 0.001, f"Parent weights sum to {_pt}"


def sample_parent_archetype(rng) -> ParentArchetype:
    names = list(ALL_PARENT_ARCHETYPES.keys())
    weights = [ALL_PARENT_ARCHETYPES[n].population_weight for n in names]
    chosen = rng.choices(names, weights=weights, k=1)[0]
    return ALL_PARENT_ARCHETYPES[chosen]


# =============================================================
# SANITY TEST
# =============================================================
if __name__ == "__main__":
    import random
    rng = random.Random(42)
    print("=" * 70)
    print("ARCHETYPE DISTRIBUTION TEST (10,000 samples)")
    print("=" * 70)
    counts = {}
    for _ in range(10_000):
        a = sample_archetype(rng)
        counts[a.name] = counts.get(a.name, 0) + 1
    for name, count in sorted(counts.items(), key=lambda x: -x[1]):
        expected = ALL_ARCHETYPES[name].population_weight * 100
        actual = count / 100
        print(f"  {name:30s}  expected: {expected:5.1f}%   actual: {actual:5.1f}%")

    print()
    print("PARENT ARCHETYPE DISTRIBUTION (10,000 samples)")
    print("=" * 70)
    p_counts = {}
    for _ in range(10_000):
        p = sample_parent_archetype(rng)
        p_counts[p.name] = p_counts.get(p.name, 0) + 1
    for name, count in sorted(p_counts.items(), key=lambda x: -x[1]):
        expected = ALL_PARENT_ARCHETYPES[name].population_weight * 100
        actual = count / 100
        print(f"  {name:30s}  expected: {expected:5.1f}%   actual: {actual:5.1f}%")