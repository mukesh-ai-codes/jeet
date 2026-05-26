"""
JEET Simulator — Step 2: Seed Catalog & Commerce

Builds on Step 1 (which seeded users). This script generates:
  - 60 cohorts assigned to mentors
  - ~380 lessons across Physics/Chemistry/Math/Biology
  - 3,000 enrollments (one per student)
  - 3,000 subscriptions
  - ~3,500 payments (some students have EMI splits)

Reads students from the DB (does not regenerate them).
"""

import logging
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import NUM_COHORTS, RANDOM_SEED, START_DATE, summary
from db import healthcheck, get_table_counts
from simulator.generators import generate_cohort, generate_commercial_records
from simulator.curriculum import generate_all_lessons
from simulator.loader import (
    bulk_insert_cohorts, bulk_insert_lessons,
    bulk_insert_enrollments, bulk_insert_subscriptions, bulk_insert_payments,
)
from sqlalchemy import text
from db import engine
from tqdm import tqdm

log = logging.getLogger("jeet.seed.catalog")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)


def fetch_required_data():
    """Read students, mentors, parents, programs, subjects from DB."""
    with engine.connect() as conn:
        # Programs (3 plans)
        programs_rows = conn.execute(text("""
            SELECT id::text, slug, name, price_inr, duration_months
            FROM programs
            ORDER BY price_inr ASC
        """)).fetchall()
        programs = [dict(zip(["id", "slug", "name", "price_inr", "duration_months"], r))
                    for r in programs_rows]

        # Subjects (4)
        subjects_rows = conn.execute(text("""
            SELECT id::text, slug FROM subjects
        """)).fetchall()
        subjects = {r[1]: r[0] for r in subjects_rows}

        # Mentors (50)
        mentors_rows = conn.execute(text("""
            SELECT id::text FROM users WHERE role = 'mentor'
        """)).fetchall()
        mentor_ids = [r[0] for r in mentors_rows]

        # Students (3,000)
        students_rows = conn.execute(text("""
            SELECT u.id::text, u.created_at, up.target_exam, up.grade
            FROM users u
            JOIN user_profiles up ON u.id = up.user_id
            WHERE u.role = 'student'
            ORDER BY u.created_at
        """)).fetchall()
        students = [dict(zip(["id", "created_at", "target_exam", "grade"], r))
                    for r in students_rows]

        # Family map: student_id → parent_id
        families_rows = conn.execute(text("""
            SELECT student_user_id::text, parent_user_id::text
            FROM families
        """)).fetchall()
        student_to_parent = {r[0]: r[1] for r in families_rows}

    return {
        "programs": programs,
        "subjects": subjects,
        "mentor_ids": mentor_ids,
        "students": students,
        "student_to_parent": student_to_parent,
    }


def main():
    summary()
    print()

    if not healthcheck():
        log.error("❌ Cannot connect to database.")
        return

    log.info("📥 Loading data from database...")
    data = fetch_required_data()
    log.info(f"   Programs:  {len(data['programs'])}")
    log.info(f"   Subjects:  {len(data['subjects'])}")
    log.info(f"   Mentors:   {len(data['mentor_ids'])}")
    log.info(f"   Students:  {len(data['students'])}")
    log.info(f"   Families:  {len(data['student_to_parent'])}")
    print()

    if not data["students"]:
        log.error("❌ No students in DB. Run 01_seed_users.py first.")
        return

    rng = random.Random(RANDOM_SEED + 1)  # Different seed than seed_users

    # =====================================================
    # PHASE 1: COHORTS
    # =====================================================
    log.info("Phase 1: Generating cohorts...")
    cohorts = []
    for i in range(NUM_COHORTS):
        # Distribute cohorts across programs (~equal split)
        program = data["programs"][i % len(data["programs"])]
        mentor_id = rng.choice(data["mentor_ids"])
        # Cohort start dates spread over 90 days before START_DATE
        cohort_start = START_DATE - timedelta(days=rng.randint(0, 90))

        cohort = generate_cohort(
            rng, program["id"], program["slug"],
            mentor_id, cohort_start, i,
        )
        cohorts.append(cohort)

    bulk_insert_cohorts(cohorts)
    log.info(f"✅ Inserted {len(cohorts)} cohorts")

    # =====================================================
    # PHASE 2: LESSONS
    # =====================================================
    log.info("Phase 2: Generating lessons (full curriculum)...")
    lessons = generate_all_lessons(
        rng,
        physics_subject_id=data["subjects"]["physics"],
        chemistry_subject_id=data["subjects"]["chemistry"],
        math_subject_id=data["subjects"]["mathematics"],
        biology_subject_id=data["subjects"]["biology"],
    )
    bulk_insert_lessons(lessons)
    log.info(f"✅ Inserted {len(lessons)} lessons")

    # =====================================================
    # PHASE 3: ENROLLMENTS + SUBSCRIPTIONS + PAYMENTS
    # =====================================================
    log.info("Phase 3: Generating enrollments + subscriptions + payments...")

    # Bucket cohorts by program for quick lookup
    cohorts_by_program = {}
    for c in cohorts:
        cohorts_by_program.setdefault(c["program_id"], []).append(c)

    program_by_id = {p["id"]: p for p in data["programs"]}

    all_enrollments = []
    all_subscriptions = []
    all_payments = []

    # Program distribution: realistic Indian EdTech share
    # Most students opt for Pro (the "Most Popular" tier in the UI)
    program_choices = [(p["slug"], p) for p in data["programs"]]
    program_weights = {
        "starter":    0.35,
        "pro":        0.50,
        "mastermind": 0.15,
    }

    for student in tqdm(data["students"], desc="  Students"):
        # Pick program weighted by realistic distribution
        slugs = [s for s, _ in program_choices]
        weights = [program_weights[s] for s in slugs]
        chosen_slug = rng.choices(slugs, weights=weights, k=1)[0]
        program = dict([(s, p) for s, p in program_choices])[chosen_slug]

        # Need archetype meta — query from a sample structure
        # Since we don't have it in DB, we'll synthesize from grade/exam
        # (the real archetype lives in memory only during seed_users.py)
        # For commercial purposes, we sample an archetype to drive payment behavior
        archetype_for_payments = rng.choices(
            ["financially_stressed", "parent_forced", "unengaged_genius",
             "disciplined_topper", "diligent_struggler", "hostel_burnout",
             "distracted_multitasker", "repeater"],
            weights=[0.14, 0.10, 0.06, 0.08, 0.15, 0.12, 0.18, 0.17],
        )[0]
        student_meta = {"archetype": archetype_for_payments}

        # Assign to a cohort of the chosen program
        cohort = rng.choice(cohorts_by_program[program["id"]])

        # Parent (if exists in family map)
        parent_id = data["student_to_parent"].get(student["id"])

        records = generate_commercial_records(
            rng=rng,
            student_user_id=student["id"],
            student_meta=student_meta,
            parent_user_id=parent_id,
            program_id=program["id"],
            program_slug=program["slug"],
            program_price_inr=program["price_inr"],
            program_duration_months=program["duration_months"],
            cohort_id=cohort["id"],
            registered_at=student["created_at"],
        )

        all_enrollments.append(records["enrollment"])
        all_subscriptions.append(records["subscription"])
        all_payments.extend(records["payments"])

    log.info(f"   Generated {len(all_enrollments)} enrollments")
    log.info(f"   Generated {len(all_subscriptions)} subscriptions")
    log.info(f"   Generated {len(all_payments)} payments")

    bulk_insert_enrollments(all_enrollments)
    log.info(f"✅ Inserted {len(all_enrollments)} enrollments")

    bulk_insert_subscriptions(all_subscriptions)
    log.info(f"✅ Inserted {len(all_subscriptions)} subscriptions")

    bulk_insert_payments(all_payments)
    log.info(f"✅ Inserted {len(all_payments)} payments")

    # =====================================================
    # SUMMARY
    # =====================================================
    print()
    log.info("=" * 60)
    log.info("CATALOG + COMMERCE SEED COMPLETE")
    log.info("=" * 60)
    counts = get_table_counts()
    for table in ["users", "user_profiles", "families", "cohorts",
                  "lessons", "enrollments", "subscriptions", "payments"]:
        log.info(f"  {table:20s} {counts[table]:>10,}")
    log.info("=" * 60)
    print()
    log.info("🎉 Commercial layer ready. JEET has cohorts, courses, and money flowing.")


if __name__ == "__main__":
    main()