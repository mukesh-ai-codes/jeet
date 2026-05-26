"""
JEET Simulator — Bulk Database Loader

Efficiently bulk-inserts generated records into PostgreSQL using
psycopg2's execute_values for 100x speed over individual INSERTs.

Design choices:
  - NO 'ON CONFLICT' clauses (loud failures > silent skips)
  - Verify by querying COUNT(*), not relying on cur.rowcount
    (rowcount is unreliable across execute_values batches in some
    psycopg2 versions)
"""

import logging
from typing import List, Dict
import psycopg2
from psycopg2.extras import execute_values
import sys
from pathlib import Path

# Add parent dir for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

log = logging.getLogger("jeet.loader")


def get_pg_connection():
    """Direct psycopg2 connection for bulk operations."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD if DB_PASSWORD else None,
    )


def _table_count(table_name: str) -> int:
    """Return exact row count for a table (source of truth)."""
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cur.fetchone()[0]
    finally:
        conn.close()


def bulk_insert_users(records: List[Dict]) -> int:
    """
    Bulk insert user records.

    Verification: counts the table directly (not cur.rowcount which is
    unreliable with execute_values across multiple batches).
    """
    if not records:
        return 0

    count_before = _table_count("users")

    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO users (
                    id, email, phone, password_hash, full_name, role,
                    avatar_url, is_active, email_verified, phone_verified,
                    last_login_at, created_at, updated_at
                ) VALUES %s
            """
            values = [
                (
                    r["id"], r["email"], r["phone"], r["password_hash"],
                    r["full_name"], r["role"], r["avatar_url"],
                    r["is_active"], r["email_verified"], r["phone_verified"],
                    r["last_login_at"], r["created_at"], r["updated_at"],
                )
                for r in records
            ]
            execute_values(cur, sql, values, page_size=500)
            conn.commit()
    finally:
        conn.close()

    count_after = _table_count("users")
    actually_inserted = count_after - count_before

    if actually_inserted != len(records):
        raise RuntimeError(
            f"Expected {len(records)} users inserted, table grew by {actually_inserted}. "
            f"Counts: before={count_before}, after={count_after}. "
            f"Possible duplicate emails/phones."
        )
    return actually_inserted


def bulk_insert_user_profiles(records: List[Dict]) -> int:
    """Bulk insert user_profiles records."""
    if not records:
        return 0

    count_before = _table_count("user_profiles")

    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO user_profiles (
                    user_id, grade, target_exam, current_score_band,
                    weak_subjects, daily_study_hours, learning_style,
                    support_preference, self_rated_ability, reported_challenges,
                    primary_goal, motivation_score, update_frequency,
                    additional_concerns, onboarding_completed, completion_percent,
                    created_at, updated_at
                ) VALUES %s
            """
            values = [
                (
                    r["user_id"], r["grade"], r["target_exam"], r["current_score_band"],
                    r["weak_subjects"], r["daily_study_hours"], r["learning_style"],
                    r["support_preference"], r["self_rated_ability"], r["reported_challenges"],
                    r["primary_goal"], r["motivation_score"], r["update_frequency"],
                    r["additional_concerns"], r["onboarding_completed"], r["completion_percent"],
                    r["created_at"], r["updated_at"],
                )
                for r in records
            ]
            execute_values(cur, sql, values, page_size=500)
            conn.commit()
    finally:
        conn.close()

    count_after = _table_count("user_profiles")
    actually_inserted = count_after - count_before

    if actually_inserted != len(records):
        raise RuntimeError(
            f"Expected {len(records)} profiles inserted, table grew by {actually_inserted}."
        )
    return actually_inserted


def bulk_insert_families(records: List[Dict]) -> int:
    """Bulk insert families records."""
    if not records:
        return 0

    count_before = _table_count("families")

    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO families (
                    id, parent_user_id, student_user_id, relationship,
                    is_primary_payer, created_at
                ) VALUES %s
            """
            values = [
                (
                    r["id"], r["parent_user_id"], r["student_user_id"],
                    r["relationship"], r["is_primary_payer"], r["created_at"],
                )
                for r in records
            ]
            execute_values(cur, sql, values, page_size=500)
            conn.commit()
    finally:
        conn.close()

    count_after = _table_count("families")
    actually_inserted = count_after - count_before

    if actually_inserted != len(records):
        raise RuntimeError(
            f"Expected {len(records)} families inserted, table grew by {actually_inserted}."
        )
    return actually_inserted
# =============================================================
# COHORT / LESSON / ENROLLMENT / SUBSCRIPTION / PAYMENT LOADERS
# =============================================================

def bulk_insert_cohorts(records: List[Dict]) -> int:
    if not records:
        return 0
    count_before = _table_count("cohorts")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO cohorts (
                    id, name, program_id, mentor_user_id, start_date, end_date,
                    max_students, current_students, is_active, created_at
                ) VALUES %s
            """
            values = [
                (r["id"], r["name"], r["program_id"], r["mentor_user_id"],
                 r["start_date"], r["end_date"], r["max_students"],
                 r["current_students"], r["is_active"], r["created_at"])
                for r in records
            ]
            execute_values(cur, sql, values, page_size=500)
            conn.commit()
    finally:
        conn.close()
    count_after = _table_count("cohorts")
    grew_by = count_after - count_before
    if grew_by != len(records):
        raise RuntimeError(f"Expected {len(records)} cohorts, table grew by {grew_by}")
    return grew_by


def bulk_insert_lessons(records: List[Dict]) -> int:
    if not records:
        return 0
    count_before = _table_count("lessons")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO lessons (
                    id, subject_id, chapter, title, description,
                    video_url, notes_url, duration_minutes,
                    difficulty_level, sequence_order, is_published, created_at
                ) VALUES %s
            """
            values = [
                (r["id"], r["subject_id"], r["chapter"], r["title"], r["description"],
                 r["video_url"], r["notes_url"], r["duration_minutes"],
                 r["difficulty_level"], r["sequence_order"], r["is_published"],
                 r["created_at"])
                for r in records
            ]
            execute_values(cur, sql, values, page_size=500)
            conn.commit()
    finally:
        conn.close()
    count_after = _table_count("lessons")
    grew_by = count_after - count_before
    if grew_by != len(records):
        raise RuntimeError(f"Expected {len(records)} lessons, table grew by {grew_by}")
    return grew_by


def bulk_insert_enrollments(records: List[Dict]) -> int:
    if not records:
        return 0
    count_before = _table_count("enrollments")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO enrollments (
                    id, student_user_id, program_id, cohort_id,
                    enrolled_at, ended_at, status, churn_reason
                ) VALUES %s
            """
            values = [
                (r["id"], r["student_user_id"], r["program_id"], r["cohort_id"],
                 r["enrolled_at"], r["ended_at"], r["status"], r["churn_reason"])
                for r in records
            ]
            execute_values(cur, sql, values, page_size=500)
            conn.commit()
    finally:
        conn.close()
    count_after = _table_count("enrollments")
    grew_by = count_after - count_before
    if grew_by != len(records):
        raise RuntimeError(f"Expected {len(records)} enrollments, table grew by {grew_by}")
    return grew_by


def bulk_insert_subscriptions(records: List[Dict]) -> int:
    if not records:
        return 0
    count_before = _table_count("subscriptions")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO subscriptions (
                    id, student_user_id, payer_user_id, program_id, enrollment_id,
                    start_date, end_date, status, auto_renew, renewal_attempts,
                    cancelled_at, cancellation_reason, created_at, updated_at
                ) VALUES %s
            """
            values = [
                (r["id"], r["student_user_id"], r["payer_user_id"], r["program_id"],
                 r["enrollment_id"], r["start_date"], r["end_date"], r["status"],
                 r["auto_renew"], r["renewal_attempts"], r["cancelled_at"],
                 r["cancellation_reason"], r["created_at"], r["updated_at"])
                for r in records
            ]
            execute_values(cur, sql, values, page_size=500)
            conn.commit()
    finally:
        conn.close()
    count_after = _table_count("subscriptions")
    grew_by = count_after - count_before
    if grew_by != len(records):
        raise RuntimeError(f"Expected {len(records)} subscriptions, table grew by {grew_by}")
    return grew_by


def bulk_insert_payments(records: List[Dict]) -> int:
    if not records:
        return 0
    count_before = _table_count("payments")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO payments (
                    id, subscription_id, payer_user_id, amount_inr, currency,
                    status, payment_method, razorpay_order_id, razorpay_payment_id,
                    razorpay_signature, idempotency_key, initiated_at, paid_at,
                    failed_at, failure_reason, refunded_amount_inr, refunded_at
                ) VALUES %s
            """
            values = [
                (r["id"], r["subscription_id"], r["payer_user_id"], r["amount_inr"],
                 r["currency"], r["status"], r["payment_method"],
                 r["razorpay_order_id"], r["razorpay_payment_id"], r["razorpay_signature"],
                 r["idempotency_key"], r["initiated_at"], r["paid_at"],
                 r["failed_at"], r["failure_reason"], r["refunded_amount_inr"],
                 r["refunded_at"])
                for r in records
            ]
            execute_values(cur, sql, values, page_size=500)
            conn.commit()
    finally:
        conn.close()
    count_after = _table_count("payments")
    grew_by = count_after - count_before
    if grew_by != len(records):
        raise RuntimeError(f"Expected {len(records)} payments, table grew by {grew_by}")
    return grew_by
# =============================================================
# EVENT / ATTENDANCE / ASSESSMENT LOADERS
# =============================================================

def bulk_insert_attendance(records: List[Dict]) -> int:
    if not records:
        return 0
    count_before = _table_count("attendance")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO attendance (
                    id, enrollment_id, lesson_id, subject_id, session_date,
                    joined, joined_at, left_at, duration_minutes,
                    engagement_score, created_at
                ) VALUES %s
            """
            values = [
                (r["id"], r["enrollment_id"], r["lesson_id"], r["subject_id"],
                 r["session_date"], r["joined"], r["joined_at"], r["left_at"],
                 r["duration_minutes"], r["engagement_score"], r["created_at"])
                for r in records
            ]
            execute_values(cur, sql, values, page_size=1000)
            conn.commit()
    finally:
        conn.close()
    count_after = _table_count("attendance")
    grew_by = count_after - count_before
    if grew_by != len(records):
        raise RuntimeError(f"Expected {len(records)} attendance, table grew by {grew_by}")
    return grew_by


def bulk_insert_assessments(records: List[Dict]) -> int:
    if not records:
        return 0
    count_before = _table_count("assessments")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO assessments (
                    id, student_user_id, subject_id, chapter, title,
                    score, max_score, time_taken_minutes,
                    difficulty_level, submitted_at
                ) VALUES %s
            """
            values = [
                (r["id"], r["student_user_id"], r["subject_id"], r["chapter"],
                 r["title"], r["score"], r["max_score"], r["time_taken_minutes"],
                 r["difficulty_level"], r["submitted_at"])
                for r in records
            ]
            execute_values(cur, sql, values, page_size=1000)
            conn.commit()
    finally:
        conn.close()
    count_after = _table_count("assessments")
    grew_by = count_after - count_before
    if grew_by != len(records):
        raise RuntimeError(f"Expected {len(records)} assessments, table grew by {grew_by}")
    return grew_by


def bulk_insert_events(records: List[Dict]) -> int:
    """
    The BIG loader. Events table will grow to ~1.4M rows.
    Uses larger page_size for throughput.
    """
    if not records:
        return 0
    count_before = _table_count("events")
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO events (
                    id, user_id, event_type, event_data, session_id,
                    ip_address, user_agent, created_at
                ) VALUES %s
            """
            from psycopg2.extras import Json
            values = [
                (r["id"], r["user_id"], r["event_type"], Json(r["event_data"]),
                 r["session_id"], r["ip_address"], r["user_agent"], r["created_at"])
                for r in records
            ]
            execute_values(cur, sql, values, page_size=2000)
            conn.commit()
    finally:
        conn.close()
    count_after = _table_count("events")
    grew_by = count_after - count_before
    if grew_by != len(records):
        raise RuntimeError(f"Expected {len(records)} events, table grew by {grew_by}")
    return grew_by