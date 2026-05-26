"""
JEET Simulator — User Generators

Generates students, parents, mentors, admins as Python dictionaries
ready for bulk insertion into PostgreSQL.

Each student gets:
  - Indian identity (region-aware name, city, school)
  - Archetype (one of 8) with behavior parameters
  - Onboarding profile (the 12-step answers, influenced by archetype)
  - A parent (linked via families)
"""

import random
import uuid
import hashlib
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple
from dataclasses import asdict

from simulator.indian_identity import (
    sample_city, sample_name, generate_email,
    generate_phone, generate_school_name, is_kota_hub,
)
from simulator.archetypes import (
    sample_archetype, sample_parent_archetype,
    ALL_ARCHETYPES, ALL_PARENT_ARCHETYPES,
)


# =============================================================
# PASSWORD HASHING
# =============================================================
# In production, use bcrypt. For synthetic data, we use a deterministic
# hash so devs can log in as any student with password "demo123!".
DEMO_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyAOudCsg/p21S"
# This is bcrypt hash of "demo123!" — fine for synthetic data only.


# =============================================================
# STUDENT GENERATOR
# =============================================================
def generate_student(rng: random.Random, registration_window_start: date,
                     registration_window_days: int = 30) -> Dict:
    """
    Generate one student with full identity + archetype + profile.

    Returns a dict with keys for:
      - user (insertable to users table)
      - profile (insertable to user_profiles table)
      - archetype_meta (kept in memory for simulator use, NOT stored in DB
        directly — used by event generator in later phases)
    """
    # Identity
    city, tier, region = sample_city(rng)
    gender = rng.choices(["male", "female"], weights=[0.62, 0.38])[0]
    # Real JEE/NEET ratio is roughly 62:38 male:female
    first_name, surname = sample_name(rng, gender, region)
    full_name = f"{first_name} {surname}"

    # Age & birth year
    grade = rng.choices([9, 10, 11, 12], weights=[0.10, 0.15, 0.35, 0.40])[0]
    # Grade 12 most common (final year prep)
    birth_year = 2026 - (grade + 5)  # grade 12 → born 2009
    birth_year += rng.randint(-1, 0)  # slight variance

    # Email & phone
    email = generate_email(rng, first_name, surname, birth_year)
    phone = generate_phone(rng)

    # School & academic context
    school = generate_school_name(rng, city)

    # Archetype assignment (this is the soul of the student)
    archetype = sample_archetype(rng)

    # Registration date (within the window)
    days_offset = rng.randint(0, registration_window_days - 1)
    registered_at = datetime.combine(
        registration_window_start + timedelta(days=days_offset),
        datetime.min.time()
    ) + timedelta(
        hours=rng.randint(8, 23),
        minutes=rng.randint(0, 59),
    )

    # Generate UUID
    user_id = str(uuid.uuid4())

    # ---------- USER RECORD ----------
    user_record = {
        "id": user_id,
        "email": email,
        "phone": phone,
        "password_hash": DEMO_PASSWORD_HASH,
        "full_name": full_name,
        "role": "student",
        "avatar_url": None,
        "is_active": True,
        "email_verified": rng.random() < 0.85,
        "phone_verified": rng.random() < 0.70,
        "last_login_at": None,  # Will be set during simulation
        "created_at": registered_at,
        "updated_at": registered_at,
    }

    # ---------- USER PROFILE (Onboarding Answers) ----------
    # These answers correlate with archetype — that's what makes ML work
    target_exam = _sample_target_exam(rng, grade)
    weak_subjects = _sample_weak_subjects(rng, archetype, target_exam)
    score_band = _sample_score_band(rng, archetype)
    challenges = _sample_challenges(rng, archetype)
    learning_style = _sample_learning_style(rng, archetype)
    support_pref = _sample_support_preference(rng, archetype)
    primary_goal = _sample_primary_goal(rng, target_exam, archetype)
    motivation = _sample_motivation_score(rng, archetype)
    update_freq = _sample_update_frequency(rng, archetype)
    additional_concerns = _sample_additional_concerns(rng, archetype)

    profile_record = {
        "user_id": user_id,
        "grade": grade,
        "target_exam": target_exam,
        "current_score_band": score_band,
        "weak_subjects": weak_subjects,
        "daily_study_hours": round(archetype.daily_study_hours_mean, 1),
        "learning_style": learning_style,
        "support_preference": support_pref,
        "self_rated_ability": _sample_self_rated_ability(rng, archetype),
        "reported_challenges": challenges,
        "primary_goal": primary_goal,
        "motivation_score": motivation,
        "update_frequency": update_freq,
        "additional_concerns": additional_concerns,
        "onboarding_completed": True,
        "completion_percent": rng.choices([100, 92, 83, 75], weights=[0.65, 0.20, 0.10, 0.05])[0],
        "created_at": registered_at,
        "updated_at": registered_at,
    }

    # ---------- META (kept in memory for downstream simulation) ----------
    meta = {
        "archetype": archetype.name,
        "city": city,
        "tier": tier,
        "region": region,
        "school": school,
        "gender": gender,
        "is_kota_hub": is_kota_hub(city),
        "registered_at": registered_at,
    }

    return {
        "user": user_record,
        "profile": profile_record,
        "meta": meta,
    }


# =============================================================
# PROFILE FIELD SAMPLERS (archetype-influenced)
# =============================================================
def _sample_target_exam(rng, grade):
    """Class 9-10 → foundation. 11-12 → JEE/NEET split."""
    if grade <= 10:
        return rng.choices(["foundation", "jee_main", "neet_ug"], weights=[0.60, 0.20, 0.20])[0]
    # Grade 11-12
    return rng.choices(
        ["jee_main", "jee_advanced", "neet_ug", "board"],
        weights=[0.40, 0.15, 0.40, 0.05],
    )[0]


def _sample_weak_subjects(rng, archetype, target_exam):
    """Multi-select weak subjects."""
    pool = ["Physics", "Chemistry", "Mathematics"] if "jee" in target_exam else ["Physics", "Chemistry", "Biology"]
    if target_exam == "foundation":
        pool = ["Physics", "Chemistry", "Mathematics", "Biology"]

    # Archetype-driven count
    if archetype.name == "diligent_struggler":
        n = rng.randint(2, 3)  # Struggles with most things
    elif archetype.name == "disciplined_topper":
        n = rng.randint(0, 1)  # Maybe one weak area
    elif archetype.name == "parent_forced":
        n = rng.randint(2, len(pool))
    else:
        n = rng.randint(1, 2)

    if n == 0:
        return []
    return rng.sample(pool, min(n, len(pool)))


def _sample_score_band(rng, archetype):
    """Self-reported current score range."""
    mean = archetype.quiz_score_mean
    if mean >= 75: return rng.choice(["80-90%", "90-100%"])
    if mean >= 60: return rng.choice(["60-70%", "70-80%"])
    if mean >= 45: return rng.choice(["40-50%", "50-60%"])
    return rng.choice(["below-40%", "40-50%"])


def _sample_challenges(rng, archetype):
    """Multi-select challenge barriers."""
    all_challenges = [
        "lack_of_understanding", "low_confidence", "exam_fear",
        "time_management", "lack_of_interest", "difficulty_in_specific_subjects",
        "peer_pressure", "family_pressure", "health_issues", "financial_stress",
    ]
    if archetype.name == "diligent_struggler":
        return rng.sample(["lack_of_understanding", "low_confidence", "difficulty_in_specific_subjects"], 2)
    if archetype.name == "hostel_burnout":
        return rng.sample(["exam_fear", "time_management", "peer_pressure", "health_issues"], 2)
    if archetype.name == "parent_forced":
        return rng.sample(["lack_of_interest", "family_pressure"], 2)
    if archetype.name == "financially_stressed":
        return rng.sample(["financial_stress", "time_management", "exam_fear"], 2)
    if archetype.name == "distracted_multitasker":
        return rng.sample(["time_management", "low_confidence"], 1)
    if archetype.name == "repeater":
        return rng.sample(["exam_fear", "low_confidence", "peer_pressure"], 2)
    # Default: 0-2 random
    n = rng.randint(0, 2)
    return rng.sample(all_challenges, n) if n > 0 else []


def _sample_learning_style(rng, archetype):
    if archetype.name == "unengaged_genius":
        return rng.choice(["video", "practice"])
    if archetype.name == "diligent_struggler":
        return rng.choices(["video", "discussion", "reading"], weights=[0.5, 0.3, 0.2])[0]
    return rng.choices(["video", "reading", "practice", "discussion"], weights=[0.50, 0.20, 0.20, 0.10])[0]


def _sample_support_preference(rng, archetype):
    if archetype.name == "diligent_struggler":
        return rng.choice(["1-on-1", "group"])
    if archetype.name == "unengaged_genius":
        return "self-study"
    if archetype.name == "hostel_burnout":
        return rng.choices(["1-on-1", "group", "self-study"], weights=[0.6, 0.3, 0.1])[0]
    return rng.choices(["1-on-1", "group", "self-study"], weights=[0.30, 0.50, 0.20])[0]


def _sample_self_rated_ability(rng, archetype):
    if archetype.quiz_score_mean >= 75:
        return rng.choices(["excellent", "good"], weights=[0.6, 0.4])[0]
    if archetype.quiz_score_mean >= 55:
        return rng.choices(["good", "average"], weights=[0.5, 0.5])[0]
    if archetype.name == "parent_forced":
        return rng.choices(["weak", "average"], weights=[0.7, 0.3])[0]
    return rng.choices(["average", "weak"], weights=[0.6, 0.4])[0]


def _sample_primary_goal(rng, target_exam, archetype):
    if target_exam == "jee_advanced":
        return rng.choice(["IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kanpur", "IIT Kharagpur"])
    if target_exam == "jee_main":
        return rng.choice(["NIT Trichy", "NIT Warangal", "BITS Pilani", "IIIT Hyderabad", "DTU"])
    if target_exam == "neet_ug":
        return rng.choice(["AIIMS Delhi", "AIIMS Bhopal", "JIPMER", "Maulana Azad Medical College", "Government Medical College"])
    if target_exam == "foundation":
        return "Strong foundation for JEE/NEET"
    return "Board exam excellence"


def _sample_motivation_score(rng, archetype):
    """1-10 self-rated motivation."""
    if archetype.name == "disciplined_topper":
        return rng.randint(8, 10)
    if archetype.name == "repeater":
        return rng.randint(7, 10)
    if archetype.name == "parent_forced":
        return rng.randint(2, 5)
    if archetype.name == "distracted_multitasker":
        return rng.randint(4, 7)
    if archetype.name == "hostel_burnout":
        return rng.randint(5, 8)  # Will decay over time in simulation
    return rng.randint(5, 8)


def _sample_update_frequency(rng, archetype):
    return rng.choices(
        ["daily", "weekly", "monthly", "as_needed"],
        weights=[0.35, 0.45, 0.15, 0.05],
    )[0]


def _sample_additional_concerns(rng, archetype):
    """Free-text seed for NLP. Archetype-flavored."""
    if archetype.name == "hostel_burnout":
        return rng.choice([
            "Stress is increasing due to hostel environment, please monitor.",
            "Wants to focus better but distractions in hostel are too many.",
            "Sleep schedule is disturbed, performance dropping.",
            None,
        ])
    if archetype.name == "parent_forced":
        return rng.choice([
            "Child shows no interest in studies, need to push.",
            "We want best for him, but he is not serious.",
            None, None,
        ])
    if archetype.name == "financially_stressed":
        return rng.choice([
            "Please consider EMI options if possible.",
            "We are stretching our budget for this. Need results.",
            None, None,
        ])
    if archetype.name == "diligent_struggler":
        return rng.choice([
            "She studies a lot but marks are not coming.",
            "Need more 1-on-1 help with fundamentals.",
            "Trying hard but losing confidence.",
            None,
        ])
    return rng.choice([
        None, None, None,
        "Please share weekly progress.",
        "Want to ensure best preparation.",
    ])


# =============================================================
# PARENT GENERATOR
# =============================================================
def generate_parent(rng: random.Random, child_meta: dict, child_record: dict,
                    registered_at: datetime) -> Dict:
    """Generate a parent linked to a student."""
    # Parent shares region & city with child
    region = child_meta["region"]
    city = child_meta["city"]

    # Father (70%) vs Mother (30%) as the registering parent
    is_father = rng.random() < 0.70
    gender = "male" if is_father else "female"

    # Parent surname matches child
    child_full_name = child_record["full_name"]
    child_surname = child_full_name.split()[-1]
    first_name, _ = sample_name(rng, gender, region)
    parent_full_name = f"{first_name} {child_surname}"

    # Email/phone
    parent_birth_year = 1975 + rng.randint(0, 15)
    email = generate_email(rng, first_name, child_surname, parent_birth_year)
    phone = generate_phone(rng)

    archetype = sample_parent_archetype(rng)

    user_id = str(uuid.uuid4())

    return {
        "user": {
            "id": user_id,
            "email": email,
            "phone": phone,
            "password_hash": DEMO_PASSWORD_HASH,
            "full_name": parent_full_name,
            "role": "parent",
            "avatar_url": None,
            "is_active": True,
            "email_verified": rng.random() < 0.90,
            "phone_verified": rng.random() < 0.85,
            "last_login_at": None,
            "created_at": registered_at,
            "updated_at": registered_at,
        },
        "archetype": archetype.name,
        "relationship": "father" if is_father else "mother",
    }


# =============================================================
# MENTOR GENERATOR
# =============================================================
MENTOR_SPECIALIZATIONS = [
    "Physics — IIT JEE",
    "Chemistry — Organic",
    "Chemistry — Inorganic & Physical",
    "Mathematics — IIT JEE",
    "Biology — NEET",
    "Physics — NEET",
    "Foundation — Class 9-10",
]


def generate_mentor(rng: random.Random) -> Dict:
    """Generate a mentor (teacher/coach) user."""
    city, tier, region = sample_city(rng)
    gender = rng.choices(["male", "female"], weights=[0.65, 0.35])[0]
    first_name, surname = sample_name(rng, gender, region)
    birth_year = 1985 + rng.randint(0, 15)

    email = generate_email(rng, first_name, surname, birth_year)
    phone = generate_phone(rng)

    user_id = str(uuid.uuid4())
    created_at = datetime.now() - timedelta(days=rng.randint(180, 1000))

    return {
        "id": user_id,
        "email": email,
        "phone": phone,
        "password_hash": DEMO_PASSWORD_HASH,
        "full_name": f"{first_name} {surname}",
        "role": "mentor",
        "avatar_url": None,
        "is_active": True,
        "email_verified": True,
        "phone_verified": True,
        "last_login_at": datetime.now() - timedelta(hours=rng.randint(1, 48)),
        "created_at": created_at,
        "updated_at": created_at,
        "_specialization": rng.choice(MENTOR_SPECIALIZATIONS),  # meta
    }


# =============================================================
# ADMIN GENERATOR
# =============================================================
def generate_admin(rng: random.Random, index: int) -> Dict:
    """Generate an admin user."""
    city, tier, region = sample_city(rng)
    gender = rng.choices(["male", "female"], weights=[0.55, 0.45])[0]
    first_name, surname = sample_name(rng, gender, region)

    user_id = str(uuid.uuid4())
    created_at = datetime.now() - timedelta(days=rng.randint(500, 1500))

    return {
        "id": user_id,
        "email": f"admin{index}@jeet.com",
        "phone": generate_phone(rng),
        "password_hash": DEMO_PASSWORD_HASH,
        "full_name": f"{first_name} {surname}",
        "role": "admin",
        "avatar_url": None,
        "is_active": True,
        "email_verified": True,
        "phone_verified": True,
        "last_login_at": datetime.now() - timedelta(hours=rng.randint(1, 24)),
        "created_at": created_at,
        "updated_at": created_at,
    }
# =============================================================
# COHORT GENERATOR
# =============================================================
COHORT_NAME_PATTERNS = [
    "{exam_track} {year} {city_anchor} {batch_letter}",
    "{exam_track}-{year} {batch_letter} ({city_anchor} Live)",
    "{exam_track} {batch_letter} — {city_anchor}",
]

BATCH_LETTERS = ["Alpha", "Beta", "Gamma", "Delta", "Sigma", "Omega",
                 "Phoenix", "Vajra", "Pioneer", "Vanguard", "Apex"]


def generate_cohort(
    rng: random.Random,
    program_id: str,
    program_slug: str,
    mentor_user_id: str,
    start_date,
    index: int,
) -> Dict:
    """Generate one cohort linked to a program and mentor."""
    exam_track = rng.choice(["JEE-2027", "JEE-2028", "NEET-2027", "NEET-2028", "Foundation-2028"])
    year = exam_track.split("-")[1]
    city_anchor = rng.choice(["Mumbai", "Delhi", "Pune", "Bangalore", "Online"])
    batch_letter = rng.choice(BATCH_LETTERS)
    pattern = rng.choice(COHORT_NAME_PATTERNS)
    name = pattern.format(
        exam_track=exam_track,
        year=year,
        city_anchor=city_anchor,
        batch_letter=batch_letter,
    )

    duration_days = {
        "starter": 90,
        "pro": 180,
        "mastermind": 365,
    }.get(program_slug, 180)

    end_date = start_date + timedelta(days=duration_days)
    max_students = rng.choice([30, 40, 50, 60])

    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "program_id": program_id,
        "mentor_user_id": mentor_user_id,
        "start_date": start_date,
        "end_date": end_date,
        "max_students": max_students,
        "current_students": 0,  # Will increment as we enroll
        "is_active": True,
        "created_at": datetime.now() - timedelta(days=rng.randint(60, 200)),
    }


# =============================================================
# ENROLLMENT + SUBSCRIPTION + PAYMENT GENERATOR
# =============================================================
def generate_commercial_records(
    rng: random.Random,
    student_user_id: str,
    student_meta: dict,
    parent_user_id,
    program_id: str,
    program_slug: str,
    program_price_inr,
    program_duration_months: int,
    cohort_id,
    registered_at: datetime,
) -> Dict:
    """
    Generate the full commercial chain for one student:
      enrollment + subscription + payment(s)

    Behavior is influenced by the student's archetype:
      - 'financially_stressed' → EMI payments, sometimes late
      - 'parent_forced' → full upfront from parent
      - 'unengaged_genius' → may pay partial then ghost
    """
    archetype = student_meta["archetype"]

    # ----- ENROLLMENT -----
    enrollment_id = str(uuid.uuid4())
    enrollment = {
        "id": enrollment_id,
        "student_user_id": student_user_id,
        "program_id": program_id,
        "cohort_id": cohort_id,
        "enrolled_at": registered_at + timedelta(hours=rng.randint(1, 48)),
        "ended_at": None,
        "status": "active",
        "churn_reason": None,
    }

    # ----- SUBSCRIPTION -----
    subscription_id = str(uuid.uuid4())
    start_date = enrollment["enrolled_at"].date()
    end_date = start_date + timedelta(days=program_duration_months * 30)

    # Most students start in 'trial' for first week, then move to 'active'
    # For synthetic data we'll just put them as 'active' from day 1
    subscription_status = "active"

    subscription = {
        "id": subscription_id,
        "student_user_id": student_user_id,
        "payer_user_id": parent_user_id if parent_user_id else student_user_id,
        "program_id": program_id,
        "enrollment_id": enrollment_id,
        "start_date": start_date,
        "end_date": end_date,
        "status": subscription_status,
        "auto_renew": rng.random() < 0.30,
        "renewal_attempts": 0,
        "cancelled_at": None,
        "cancellation_reason": None,
        "created_at": enrollment["enrolled_at"],
        "updated_at": enrollment["enrolled_at"],
    }

    # ----- PAYMENT(S) -----
    # Decide payment style based on archetype
    payments = []

    if archetype == "financially_stressed":
        # 60% pay in EMIs, 40% pay full but late
        if rng.random() < 0.60:
            # 2-3 EMIs
            num_emis = rng.choice([2, 3])
            installment_amount = round(float(program_price_inr) / num_emis, 2)
            for i in range(num_emis):
                pay_date = enrollment["enrolled_at"] + timedelta(days=i * 30 + rng.randint(0, 7))
                status = "captured" if rng.random() < 0.90 else "failed"
                payments.append(_build_payment(
                    rng, subscription_id, subscription["payer_user_id"],
                    installment_amount, status, pay_date,
                ))
        else:
            # Full but delayed
            pay_date = enrollment["enrolled_at"] + timedelta(days=rng.randint(3, 14))
            status = "captured" if rng.random() < 0.95 else "failed"
            payments.append(_build_payment(
                rng, subscription_id, subscription["payer_user_id"],
                float(program_price_inr), status, pay_date,
            ))

    elif archetype == "parent_forced":
        # Always full upfront, immediate, no issues
        pay_date = enrollment["enrolled_at"] + timedelta(hours=rng.randint(1, 24))
        payments.append(_build_payment(
            rng, subscription_id, subscription["payer_user_id"],
            float(program_price_inr), "captured", pay_date,
        ))

    elif archetype == "unengaged_genius":
        # Sometimes pay partial, sometimes full
        if rng.random() < 0.20:
            # Initial payment only, will likely not renew
            pay_date = enrollment["enrolled_at"] + timedelta(hours=rng.randint(1, 12))
            payments.append(_build_payment(
                rng, subscription_id, subscription["payer_user_id"],
                float(program_price_inr) * 0.5, "captured", pay_date,
            ))
        else:
            pay_date = enrollment["enrolled_at"] + timedelta(hours=rng.randint(1, 24))
            payments.append(_build_payment(
                rng, subscription_id, subscription["payer_user_id"],
                float(program_price_inr), "captured", pay_date,
            ))

    else:
        # Default: most students pay upfront with rare failures
        pay_date = enrollment["enrolled_at"] + timedelta(hours=rng.randint(1, 72))
        # First attempt: 92% success rate
        if rng.random() < 0.92:
            payments.append(_build_payment(
                rng, subscription_id, subscription["payer_user_id"],
                float(program_price_inr), "captured", pay_date,
            ))
        else:
            # First failed, second succeeded
            payments.append(_build_payment(
                rng, subscription_id, subscription["payer_user_id"],
                float(program_price_inr), "failed", pay_date,
            ))
            retry_date = pay_date + timedelta(hours=rng.randint(2, 48))
            payments.append(_build_payment(
                rng, subscription_id, subscription["payer_user_id"],
                float(program_price_inr), "captured", retry_date,
            ))

    return {
        "enrollment": enrollment,
        "subscription": subscription,
        "payments": payments,
    }


def _build_payment(rng, subscription_id, payer_user_id, amount, status, paid_at):
    """Helper to build a single payment record."""
    method = rng.choices(
        ["upi", "card", "netbanking", "wallet"],
        weights=[0.55, 0.25, 0.15, 0.05],
    )[0]

    return {
        "id": str(uuid.uuid4()),
        "subscription_id": subscription_id,
        "payer_user_id": payer_user_id,
        "amount_inr": round(amount, 2),
        "currency": "INR",
        "status": status,
        "payment_method": method,
        "razorpay_order_id": f"order_{uuid.uuid4().hex[:14]}",
        "razorpay_payment_id": f"pay_{uuid.uuid4().hex[:14]}" if status == "captured" else None,
        "razorpay_signature": uuid.uuid4().hex if status == "captured" else None,
        "idempotency_key": uuid.uuid4().hex,
        "initiated_at": paid_at - timedelta(minutes=rng.randint(1, 5)),
        "paid_at": paid_at if status == "captured" else None,
        "failed_at": paid_at if status == "failed" else None,
        "failure_reason": rng.choice([
            "Insufficient balance",
            "Card declined by issuer",
            "Authentication failed",
            "Bank server timeout",
        ]) if status == "failed" else None,
        "refunded_amount_inr": 0,
        "refunded_at": None,
    }