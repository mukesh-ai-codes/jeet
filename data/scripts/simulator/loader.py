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