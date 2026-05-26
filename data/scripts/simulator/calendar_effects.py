"""
JEET Simulator — Calendar Effects Engine

Models how the Indian calendar affects EdTech student behavior:
  - Sundays boost engagement (mock test culture)
  - Diwali / Holi cause major dips
  - Board exam season (Feb-Mar) shifts focus
  - Exam crunch (last 30 days) doubles intensity
  - Weekends have different patterns by archetype

This module returns multipliers (typically 0.4 to 2.0) that adjust
the baseline daily behaviors of each student.
"""

from datetime import date, timedelta
from typing import Dict, Set


# =============================================================
# INDIAN HOLIDAY CALENDAR (simulation window: 2026-01-01 to 2026-04-30)
# =============================================================
# Major holidays in the 120-day window starting Jan 1, 2026
INDIAN_HOLIDAYS = {
    # Major engagement-killers (drop to 30-50%)
    date(2026, 1, 14): ("Makar Sankranti / Pongal", 0.55),
    date(2026, 1, 26): ("Republic Day", 0.65),
    date(2026, 2, 14): ("Vasant Panchami", 0.75),
    date(2026, 3, 3):  ("Holi", 0.40),  # Major dip
    date(2026, 3, 4):  ("Holi (Day 2)", 0.45),
    date(2026, 3, 17): ("Holi 2", 0.60),  # Regional variation
    date(2026, 3, 21): ("Ram Navami", 0.65),
    date(2026, 4, 14): ("Baisakhi / Ambedkar Jayanti", 0.65),
}


# =============================================================
# BOARD EXAM WINDOW
# =============================================================
# CBSE/State boards happen Feb-March
# JEE/NEET aspirants in Class 12 split focus
BOARD_EXAM_START = date(2026, 2, 15)
BOARD_EXAM_END = date(2026, 3, 31)


# =============================================================
# CORE CALENDAR EFFECT FUNCTIONS
# =============================================================

def get_holiday_multiplier(day: date) -> float:
    """Return engagement multiplier for a holiday (0.4–1.0 typical)."""
    if day in INDIAN_HOLIDAYS:
        return INDIAN_HOLIDAYS[day][1]
    # Day after major holiday is also reduced
    yesterday = day - timedelta(days=1)
    if yesterday in INDIAN_HOLIDAYS:
        return min(0.85, INDIAN_HOLIDAYS[yesterday][1] + 0.20)
    return 1.0


def get_weekday_multiplier(day: date, archetype_name: str) -> float:
    """
    Engagement varies by day-of-week.
    Monday = 0 ... Sunday = 6 in Python.
    """
    weekday = day.weekday()

    # Sunday — Mock Test Day (Indian coaching tradition)
    # Strong boost across all archetypes — this is the cultural reality
    if weekday == 6:
        if archetype_name in ("disciplined_topper", "repeater", "diligent_struggler",
                              "financially_stressed"):
            return 1.65  # Heavy Sunday warriors
        if archetype_name == "unengaged_genius":
            return 1.80  # Pure weekend crammer
        if archetype_name == "hostel_burnout":
            return 1.45  # Slightly less due to burnout
        if archetype_name == "parent_forced":
            return 1.30  # Parent watching closely on Sunday
        return 1.50  # Default — everyone gets pulled into Sunday mock culture

    # Saturday — variable
    if weekday == 5:
        if archetype_name == "distracted_multitasker":
            return 0.65  # Gaming weekend
        if archetype_name == "parent_forced":
            return 0.70  # Performative drop on weekend
        if archetype_name == "unengaged_genius":
            return 1.40
        return 0.95

    # Mid-week (Tue-Thu) — peak study days
    if weekday in (1, 2, 3):
        return 1.05

    # Monday — slow start
    if weekday == 0:
        if archetype_name == "hostel_burnout":
            return 0.85
        return 0.95

    # Friday — winding down
    if weekday == 4:
        if archetype_name == "distracted_multitasker":
            return 0.85
        return 0.92

    return 1.0


def get_board_exam_effect(day: date, grade: int, target_exam: str) -> float:
    """
    Class 12 students prepping for JEE/NEET get pulled into board exam prep.
    Their JEET engagement DROPS during board season because they shift focus.
    """
    if not (BOARD_EXAM_START <= day <= BOARD_EXAM_END):
        return 1.0

    if grade != 12:
        return 1.0

    if target_exam in ("board", "foundation"):
        return 1.20  # Boards-focused students engage MORE

    # JEE/NEET Class 12 students split focus
    return 0.65


def get_exam_proximity_boost(
    day: date,
    target_exam_date: date,
) -> float:
    """
    Engagement spikes as the target exam approaches.
    Last 30 days = 1.5×, last 14 days = 1.8×, last 7 days = 2.0×
    """
    days_to_exam = (target_exam_date - day).days

    if days_to_exam < 0:
        return 0.30  # Post-exam crash
    if days_to_exam <= 7:
        return 2.00
    if days_to_exam <= 14:
        return 1.80
    if days_to_exam <= 30:
        return 1.50
    if days_to_exam <= 60:
        return 1.20

    return 1.0


def get_seasonal_multiplier(day: date) -> float:
    """
    Indian seasonal effects on student energy.
    Summer (Mar-May): rising heat = mild engagement drop in Tier-2/3
    Winter (Dec-Feb): peak study weather in North India
    """
    month = day.month
    if month in (4, 5):
        return 0.92
    if month in (12, 1):
        return 1.05
    return 1.0


# =============================================================
# COMPOSITE CALENDAR EFFECT
# =============================================================

def composite_calendar_multiplier(
    day: date,
    archetype_name: str,
    grade: int,
    target_exam: str,
    target_exam_date: date = None,
) -> float:
    """
    Final multiplier for daily engagement based on all calendar factors.

    Range typically: 0.3 (Holi day) to 2.0 (week before exam).
    Default neutral day: ~1.0.
    """
    m = 1.0
    m *= get_holiday_multiplier(day)
    m *= get_weekday_multiplier(day, archetype_name)
    m *= get_board_exam_effect(day, grade, target_exam)
    m *= get_seasonal_multiplier(day)
    if target_exam_date:
        m *= get_exam_proximity_boost(day, target_exam_date)

    # Cap extremes
    return max(0.25, min(2.5, m))


# =============================================================
# SANITY TEST
# =============================================================
if __name__ == "__main__":
    from datetime import date, timedelta
    print("=" * 70)
    print("CALENDAR EFFECTS SANITY TEST")
    print("=" * 70)

    start = date(2026, 1, 1)
    print(f"\n{'Date':<14} {'Day':<10} {'Archetype':<25} {'Multiplier':>10}")
    print("-" * 70)

    test_dates = [
        date(2026, 1, 1),   # Thursday — normal
        date(2026, 1, 4),   # Sunday — mock test day
        date(2026, 1, 14),  # Sankranti
        date(2026, 1, 26),  # Republic Day
        date(2026, 2, 20),  # Board exam window
        date(2026, 3, 3),   # Holi
        date(2026, 3, 8),   # Sunday after Holi
        date(2026, 4, 15),  # Just after Baisakhi
    ]

    for d in test_dates:
        day_name = d.strftime("%A")
        for arch in ["disciplined_topper", "distracted_multitasker", "hostel_burnout"]:
            m = composite_calendar_multiplier(d, arch, grade=12, target_exam="jee_main")
            tag = ""
            if d in INDIAN_HOLIDAYS:
                tag = f" ← {INDIAN_HOLIDAYS[d][0]}"
            print(f"{str(d):<14} {day_name:<10} {arch:<25} {m:>8.2f}{tag}")
        print()