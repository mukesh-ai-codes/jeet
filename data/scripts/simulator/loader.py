"""
JEET Simulator — Bulk Database Loader

Efficiently bulk-inserts generated records into PostgreSQL using
psycopg2's execute_values for 100x speed over individual INSERTs.
"""

import logging
from typing import List, Dict
import psycopg2
from psycopg2.extras import execute_values, Json
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


def bulk_insert_users(records: List[Dict]) -> int:
    """Bulk insert user records into users table."""
    if not records:
        return 0
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO users (
                    id, email, phone, password_hash, full_name, role,
                    avatar_url, is_active, email_verified, phone_verified,
                    last_login_at, created_at, updated_at
                ) VALUES %s
                ON CONFLICT (email) DO NOTHING
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
            return cur.rowcount
    finally:
        conn.close()


def bulk_insert_user_profiles(records: List[Dict]) -> int:
    """Bulk insert user_profiles records."""
    if not records:
        return 0
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
                ON CONFLICT (user_id) DO NOTHING
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
            return cur.rowcount
    finally:
        conn.close()


def bulk_insert_families(records: List[Dict]) -> int:
    """Bulk insert families records."""
    if not records:
        return 0
    conn = get_pg_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO families (
                    id, parent_user_id, student_user_id, relationship,
                    is_primary_payer, created_at
                ) VALUES %s
                ON CONFLICT (parent_user_id, student_user_id) DO NOTHING
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
            return cur.rowcount
    finally:
        conn.close()