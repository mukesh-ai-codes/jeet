"""
JEET Simulator — Step 1: Seed Users (Students, Parents, Mentors, Admins)

Generates and bulk-inserts:
  - 3,000 students with archetype-driven profiles
  - ~2,550 parents linked via families
  - 50 mentors
  - 5 admins

Idempotent: truncates transactional tables before seeding.
"""

import logging
import random
import sys
import uuid
from pathlib import Path

# Path setup
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    NUM_STUDENTS, NUM_MENTORS, NUM_ADMINS, RANDOM_SEED,
    START_DATE, summary,
)
from db import healthcheck, get_table_counts, truncate_all_data
from simulator.indian_identity import reset_uniqueness_counters
from simulator.generators import (
    generate_student, generate_parent,
    generate_mentor, generate_admin,
)
from simulator.loader import (
    bulk_insert_users, bulk_insert_user_profiles, bulk_insert_families,
)
from tqdm import tqdm

log = logging.getLogger("jeet.seed")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)


def main(clean_first: bool = True):
    summary()
    print()

    if not healthcheck():
        log.error("❌ Cannot connect to database. Aborting.")
        return

    # Idempotency: clean transactional tables before seeding.
    if clean_first:
        log.info("🧹 Cleaning existing transactional data...")
        truncate_all_data(confirm=True)
        log.info("✅ Database is clean. Starting fresh seed.")
        print()

    # Reset uniqueness counters (CRITICAL: must be called before generation)
    reset_uniqueness_counters()

    rng = random.Random(RANDOM_SEED)

    # =====================================================
    # PHASE 1: GENERATE ALL STUDENTS
    # =====================================================
    log.info("Phase 1: Generating students...")
    students = []
    for _ in tqdm(range(NUM_STUDENTS), desc="  Students"):
        s = generate_student(rng, START_DATE, registration_window_days=30)
        students.append(s)
    log.info(f"✅ Generated {len(students)} students")

    # =====================================================
    # PHASE 2: GENERATE PARENTS
    # =====================================================
    log.info("Phase 2: Generating parents and family links...")
    parents = []
    family_links = []

    for s in tqdm(students, desc="  Parents"):
        if rng.random() < 0.85:  # 85% of students have parent accounts
            p = generate_parent(
                rng,
                child_meta=s["meta"],
                child_record=s["user"],
                registered_at=s["user"]["created_at"],
            )
            parents.append(p)
            family_links.append({
                "id": str(uuid.uuid4()),
                "parent_user_id": p["user"]["id"],
                "student_user_id": s["user"]["id"],
                "relationship": p["relationship"],
                "is_primary_payer": True,
                "created_at": s["user"]["created_at"],
            })

    log.info(f"✅ Generated {len(parents)} parents and {len(family_links)} family links")

    # =====================================================
    # PHASE 3: GENERATE MENTORS
    # =====================================================
    log.info("Phase 3: Generating mentors...")
    mentors = [generate_mentor(rng) for _ in tqdm(range(NUM_MENTORS), desc="  Mentors")]
    log.info(f"✅ Generated {len(mentors)} mentors")

    # =====================================================
    # PHASE 4: GENERATE ADMINS
    # =====================================================
    log.info("Phase 4: Generating admins...")
    admins = [generate_admin(rng, i + 1) for i in range(NUM_ADMINS)]
    log.info(f"✅ Generated {len(admins)} admins")

    # =====================================================
    # PHASE 5: BULK INSERT — USERS
    # =====================================================
    log.info("Phase 5: Bulk inserting users into database...")

    all_user_records = (
        [s["user"] for s in students] +
        [p["user"] for p in parents] +
        [{k: v for k, v in m.items() if not k.startswith("_")} for m in mentors] +
        admins
    )
    log.info(f"  Inserting {len(all_user_records)} users...")
    inserted = bulk_insert_users(all_user_records)
    log.info(f"✅ Inserted {inserted} users")

    # =====================================================
    # PHASE 6: BULK INSERT — USER PROFILES
    # =====================================================
    log.info("Phase 6: Bulk inserting user profiles...")
    profile_records = [s["profile"] for s in students]
    inserted = bulk_insert_user_profiles(profile_records)
    log.info(f"✅ Inserted {inserted} user profiles")

    # =====================================================
    # PHASE 7: BULK INSERT — FAMILIES
    # =====================================================
    log.info("Phase 7: Bulk inserting family links...")
    inserted = bulk_insert_families(family_links)
    log.info(f"✅ Inserted {inserted} family links")

    # =====================================================
    # SUMMARY
    # =====================================================
    print()
    log.info("=" * 60)
    log.info("SEED COMPLETE — Final row counts:")
    log.info("=" * 60)
    counts = get_table_counts()
    for table in ["users", "families", "user_profiles", "programs", "subjects"]:
        log.info(f"  {table:20s} {counts[table]:>10,}")
    log.info("=" * 60)
    print()
    log.info("🎉 JEET is now populated with realistic Indian students!")
    log.info("   Check TablePlus → users table to see them.")


if __name__ == "__main__":
    main()