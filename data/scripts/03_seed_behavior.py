"""
JEET Simulator — Step 3: Seed 120-Day Behavioral Universe

The cornerstone simulation. For each of 3,000 students, runs a day-by-day
behavioral loop that:
  - Decides daily login/study/quiz/doubt behaviors
  - Generates realistic events (~1.4M rows total)
  - Records attendance and assessments
  - Evolves student psychological state
  - Resolves churn outcomes
  - Updates enrollment + subscription statuses

This is THE dataset ML models will train on.
"""

import logging
import random
import sys
import uuid
from pathlib import Path
from datetime import date, timedelta, datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import NUM_DAYS, RANDOM_SEED, START_DATE, summary
from db import healthcheck, get_table_counts, engine
from sqlalchemy import text

from simulator.archetypes import ALL_ARCHETYPES, sample_archetype
from simulator.student_state import (
    StudentState, initialize_state_from_archetype,
    evolve_state_after_active_day, evolve_state_after_inactive_day,
    apply_mentor_intervention_boost, apply_payment_failure_shock,
    evaluate_churn_risk, apply_financial_churn_check,
)
from simulator.behavior_engine import (
    decide_will_login_today, decide_session_duration, decide_is_late_night,
    decide_lessons_completed, decide_quiz_attempted, decide_quiz_score,
    decide_doubt_asked, decide_mentor_intervention,
)
from simulator.event_factory import (
    generate_daily_events, generate_attendance_record, generate_assessment_record,
)
from simulator.loader import (
    bulk_insert_events, bulk_insert_attendance, bulk_insert_assessments,
)
from tqdm import tqdm

log = logging.getLogger("jeet.seed.behavior")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)


# =============================================================
# DATA LOADER
# =============================================================
def load_simulation_inputs():
    """Read everything needed from DB to run the simulation."""
    log.info("📥 Loading simulation inputs from database...")

    with engine.connect() as conn:
        # Students with profile & enrollment data
        students_rows = conn.execute(text("""
            SELECT
                u.id::text AS user_id,
                up.grade,
                up.target_exam,
                up.weak_subjects,
                e.id::text AS enrollment_id,
                e.cohort_id::text AS cohort_id,
                e.enrolled_at,
                u.created_at AS registered_at
            FROM users u
            JOIN user_profiles up ON u.id = up.user_id
            JOIN enrollments e ON e.student_user_id = u.id
            WHERE u.role = 'student'
        """)).fetchall()
        students = [
            dict(zip(
                ["user_id", "grade", "target_exam", "weak_subjects",
                 "enrollment_id", "cohort_id", "enrolled_at", "registered_at"],
                r
            ))
            for r in students_rows
        ]

        # All lessons grouped by subject for sampling
        lessons_rows = conn.execute(text("""
            SELECT id::text, subject_id::text FROM lessons WHERE is_published = TRUE
        """)).fetchall()
        lesson_ids_all = [r[0] for r in lessons_rows]
        lessons_by_subject = defaultdict(list)
        for lid, sid in lessons_rows:
            lessons_by_subject[sid].append(lid)

        # Subjects (slug -> id)
        subjects_rows = conn.execute(text("""
            SELECT id::text, slug FROM subjects
        """)).fetchall()
        subject_id_by_slug = {r[1]: r[0] for r in subjects_rows}
        subject_slug_by_id = {r[0]: r[1] for r in subjects_rows}

    log.info(f"   Students:    {len(students):,}")
    log.info(f"   Lessons:     {len(lesson_ids_all):,}")
    log.info(f"   Subjects:    {len(subject_id_by_slug)}")
    return {
        "students": students,
        "lesson_ids_all": lesson_ids_all,
        "lessons_by_subject": lessons_by_subject,
        "subject_id_by_slug": subject_id_by_slug,
        "subject_slug_by_id": subject_slug_by_id,
    }


# =============================================================
# CHURN OUTCOME UPDATE
# =============================================================
def write_churn_outcomes_to_db(students_with_state):
    """
    After simulation completes, update enrollments + subscriptions for
    students who churned during the simulation window.
    """
    log.info("📝 Writing churn outcomes back to enrollments + subscriptions...")

    churned_updates = []
    for stu, state in students_with_state:
        if state.final_status != "active" and state.churn_day is not None:
            churn_date = START_DATE + timedelta(days=state.churn_day)
            churned_updates.append({
                "enrollment_id": stu["enrollment_id"],
                "user_id": stu["user_id"],
                "status": state.final_status,
                "churn_day": state.churn_day,
                "churn_date": churn_date,
                "churn_reason": state.churn_reason,
            })

    if not churned_updates:
        log.info("   No churn outcomes to update.")
        return 0

    with engine.begin() as conn:
        for u in churned_updates:
            # Determine enrollment + subscription status from churn reason
            if u["status"] == "churned_financial":
                enroll_status = "cancelled"
                sub_status = "cancelled"
            elif u["status"] == "paused":
                enroll_status = "paused"
                sub_status = "paused"
            else:
                enroll_status = "churned"
                sub_status = "churned"

            # Update enrollment
            conn.execute(text("""
                UPDATE enrollments
                   SET status = :status,
                       ended_at = :ended_at,
                       churn_reason = :reason
                 WHERE id = :enrollment_id
            """), {
                "status": enroll_status,
                "ended_at": u["churn_date"],
                "reason": u["churn_reason"],
                "enrollment_id": u["enrollment_id"],
            })

            # Update subscription
            conn.execute(text("""
                UPDATE subscriptions
                   SET status = :status,
                       cancelled_at = :cancelled_at,
                       cancellation_reason = :reason,
                       updated_at = NOW()
                 WHERE student_user_id = :user_id
            """), {
                "status": sub_status,
                "cancelled_at": u["churn_date"],
                "reason": u["churn_reason"],
                "user_id": u["user_id"],
            })

    log.info(f"   ✅ Updated {len(churned_updates)} students' enrollment + subscription status")
    return len(churned_updates)


# =============================================================
# MAIN SIMULATION
# =============================================================
def main():
    summary()
    print()

    if not healthcheck():
        log.error("❌ Cannot connect to database.")
        return

    # Check we have students seeded
    counts = get_table_counts()
    if counts["enrollments"] == 0:
        log.error("❌ No enrollments found. Run 01_seed_users.py and 02_seed_catalog_and_commerce.py first.")
        return

    if counts["events"] > 0:
        log.warning(f"⚠️  Found {counts['events']:,} existing events. Truncating before re-simulating...")
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE events, attendance, assessments CASCADE"))
        log.info("   Cleared events, attendance, assessments tables")

    # Load inputs
    inputs = load_simulation_inputs()
    students = inputs["students"]
    lesson_ids_all = inputs["lesson_ids_all"]
    subject_id_by_slug = inputs["subject_id_by_slug"]
    subject_slug_by_id = inputs["subject_slug_by_id"]

    if not students:
        log.error("❌ No students loaded. Aborting.")
        return

    rng_master = random.Random(RANDOM_SEED + 42)

    # ============================================================
    # PHASE 1: Initialize student states + assign archetypes
    # ============================================================
    log.info("Phase 1: Initializing 3,000 student behavioral states...")

    student_states = []
    archetype_list = list(ALL_ARCHETYPES.values())
    archetype_weights = [a.population_weight for a in archetype_list]

    for stu in students:
        # Each student gets a deterministic but unique RNG
        local_rng = random.Random(hash(stu["user_id"]) & 0xFFFFFFFF)

        # Sample archetype with realistic distribution
        archetype = rng_master.choices(archetype_list, weights=archetype_weights, k=1)[0]
        state = initialize_state_from_archetype(stu["user_id"], archetype)
        student_states.append((stu, archetype, state, local_rng))

    log.info(f"   ✅ Initialized {len(student_states)} states")

    # ============================================================
    # PHASE 2: 120-Day Behavioral Loop
    # ============================================================
    log.info(f"Phase 2: Running {NUM_DAYS}-day behavioral simulation...")
    log.info("   This will take 5-10 minutes. Watch the magic happen.")
    print()

    all_events = []
    all_attendance = []
    all_assessments = []

    # Target exam date for proximity calculations
    # JEE Main is typically late April / early May
    target_exam_date = START_DATE + timedelta(days=NUM_DAYS + 30)

    # Daily progress with tqdm
    for day_idx in tqdm(range(NUM_DAYS), desc="  Days simulated"):
        current_date = START_DATE + timedelta(days=day_idx)

        for stu, archetype, state, local_rng in student_states:

            # Skip if churned before this day
            if state.final_status != "active":
                continue

            # Skip if student hasn't registered yet (registration window: Jan 1-30)
            stu_registered_date = stu["registered_at"].date() if hasattr(stu["registered_at"], "date") else stu["registered_at"]
            if current_date < stu_registered_date:
                continue

            # ----- DECIDE: WILL THEY LOGIN TODAY? -----
            will_login = decide_will_login_today(
                local_rng, state, archetype, current_date,
                stu["grade"], stu["target_exam"], target_exam_date,
            )

            if will_login:
                # Active day: generate session events
                session_min = decide_session_duration(local_rng, state, archetype)
                is_late_night = decide_is_late_night(local_rng, state, archetype)
                lessons_done = decide_lessons_completed(local_rng, state, archetype, session_min)
                quiz_attempted = decide_quiz_attempted(local_rng, state, archetype, day_idx)
                quiz_score = decide_quiz_score(local_rng, state, archetype) if quiz_attempted else None
                doubts = decide_doubt_asked(local_rng, state, archetype, session_min)

                # Generate events
                weak_subjects = stu["weak_subjects"] or []
                events = generate_daily_events(
                    rng=local_rng,
                    student_user_id=stu["user_id"],
                    day=current_date,
                    session_minutes=session_min,
                    lessons_completed=lessons_done,
                    quiz_attempted=quiz_attempted,
                    quiz_score=quiz_score,
                    doubts_asked=doubts,
                    is_late_night=is_late_night,
                    available_lesson_ids=lesson_ids_all,
                    available_subject_ids=subject_id_by_slug,
                    weak_subjects=weak_subjects,
                )
                all_events.extend(events)

                # If quiz attempted, also create assessment record
                if quiz_attempted and quiz_score is not None:
                    # Pick subject (bias toward weak)
                    if weak_subjects and local_rng.random() < 0.55:
                        weak_lower = [w.lower() for w in weak_subjects]
                        candidates = [s for s in subject_id_by_slug if s in weak_lower]
                        subj_slug = local_rng.choice(candidates) if candidates else local_rng.choice(list(subject_id_by_slug.keys()))
                    else:
                        subj_slug = local_rng.choice(list(subject_id_by_slug.keys()))

                    is_mock = (current_date.weekday() == 6 and local_rng.random() < 0.4)
                    submitted_at = datetime.combine(current_date, datetime.min.time())
                    submitted_at = submitted_at.replace(hour=local_rng.randint(10, 20),
                                                       minute=local_rng.randint(0, 59))

                    assess = generate_assessment_record(
                        local_rng, stu["user_id"],
                        subject_id_by_slug[subj_slug], subj_slug,
                        quiz_score, submitted_at, is_mock=is_mock,
                    )
                    all_assessments.append(assess)

                # Attendance: simulate live session 3x per week (Mon, Wed, Fri)
                if current_date.weekday() in (0, 2, 4):
                    # 3 sessions per week, randomly pick a lesson + subject
                    if lesson_ids_all:
                        lesson_id = local_rng.choice(lesson_ids_all)
                        # Map back to subject via lookup
                        subject_id = local_rng.choice(list(subject_id_by_slug.values()))
                        joined = local_rng.random() < (state.engagement_score / 100.0)
                        att = generate_attendance_record(
                            local_rng, stu["enrollment_id"], lesson_id, subject_id,
                            current_date, joined, state.engagement_score, archetype.name,
                        )
                        all_attendance.append(att)

                # Mentor intervention check
                mentor_intervened = decide_mentor_intervention(
                    local_rng, state, archetype, day_idx,
                )
                if mentor_intervened:
                    apply_mentor_intervention_boost(state)

                # State evolution
                cal_mult = 1.0  # already factored into login decision
                evolve_state_after_active_day(
                    state, archetype,
                    session_duration_min=session_min,
                    lessons_completed=lessons_done,
                    quiz_attempted=quiz_attempted,
                    quiz_score=quiz_score,
                    late_night=is_late_night,
                    calendar_multiplier=cal_mult,
                )

            else:
                # Inactive day
                evolve_state_after_inactive_day(state, archetype)

            # ----- CHURN CHECK (academic + burnout) -----
            churn_reason = evaluate_churn_risk(state, day_idx)
            if churn_reason:
                if churn_reason in ("academic_disengagement", "ghosted", "confidence_collapse"):
                    state.final_status = "churned_academic"
                elif churn_reason == "burnout":
                    state.final_status = "paused"
                else:
                    state.final_status = "churned_academic"
                state.churn_day = day_idx
                state.churn_reason = churn_reason

            # ----- FINANCIAL CHURN CHECK (separate trigger) -----
            elif apply_financial_churn_check(state, archetype, local_rng, day_idx):
                state.final_status = "churned_financial"
                state.churn_day = day_idx
                state.churn_reason = "financial_non_payment"

        # Periodic flush to avoid memory blowup
        if len(all_events) > 200_000:
            log.info(f"   Day {day_idx}: flushing {len(all_events):,} events to DB...")
            bulk_insert_events(all_events)
            all_events = []
        if len(all_attendance) > 50_000:
            bulk_insert_attendance(all_attendance)
            all_attendance = []
        if len(all_assessments) > 20_000:
            bulk_insert_assessments(all_assessments)
            all_assessments = []

    # ============================================================
    # PHASE 3: Final flush
    # ============================================================
    print()
    log.info("Phase 3: Flushing remaining records to database...")
    if all_events:
        bulk_insert_events(all_events)
        log.info(f"   ✅ Inserted {len(all_events):,} remaining events")
    if all_attendance:
        bulk_insert_attendance(all_attendance)
        log.info(f"   ✅ Inserted {len(all_attendance):,} remaining attendance records")
    if all_assessments:
        bulk_insert_assessments(all_assessments)
        log.info(f"   ✅ Inserted {len(all_assessments):,} remaining assessment records")

    # ============================================================
    # PHASE 4: Update churn outcomes in DB
    # ============================================================
    print()
    students_with_state = [(stu, state) for stu, archetype, state, rng in student_states]
    write_churn_outcomes_to_db(students_with_state)

    # ============================================================
    # PHASE 5: Final summary
    # ============================================================
    print()
    log.info("=" * 70)
    log.info("BEHAVIORAL SIMULATION COMPLETE")
    log.info("=" * 70)

    counts = get_table_counts()
    for table in ["users", "user_profiles", "families", "cohorts", "lessons",
                  "enrollments", "subscriptions", "payments",
                  "attendance", "assessments", "events"]:
        log.info(f"  {table:20s} {counts[table]:>12,}")
    log.info("=" * 70)

    # Churn breakdown
    churn_breakdown = defaultdict(int)
    for _, _, state, _ in student_states:
        churn_breakdown[state.final_status] += 1

    print()
    log.info("Final student status breakdown:")
    total = sum(churn_breakdown.values())
    for status, count in sorted(churn_breakdown.items(), key=lambda x: -x[1]):
        pct = count * 100 / total
        log.info(f"  {status:25s} {count:>5,} ({pct:>5.1f}%)")
    log.info("=" * 70)

    print()
    log.info("🎉 JEET behavioral universe is complete. ML can now learn from real patterns.")
    log.info("   Run validation queries in TablePlus to inspect the data.")


if __name__ == "__main__":
    main()