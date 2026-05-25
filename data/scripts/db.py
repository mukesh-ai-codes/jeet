"""
JEET Simulator — Database Connection Module

Provides connection management to PostgreSQL.
Uses SQLAlchemy for connection pooling and psycopg2 for raw bulk inserts.
"""

import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

# --------------------------------------------------------
# Logging Setup
# --------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("jeet.db")

# --------------------------------------------------------
# Engine (connection pool)
# --------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,  # Set True to see every SQL query (verbose)
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_session():
    """Context manager for safe DB sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        log.error(f"DB session error: {e}")
        raise
    finally:
        session.close()


def healthcheck() -> bool:
    """Verify database connectivity."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        log.error(f"DB healthcheck failed: {e}")
        return False


def get_table_counts() -> dict:
    """Return row counts for all JEET tables."""
    tables = [
        "users", "families", "user_profiles",
        "programs", "subjects", "cohorts", "lessons",
        "enrollments", "attendance", "assessments", "events",
        "subscriptions", "payments", "risk_scores",
    ]
    counts = {}
    with engine.connect() as conn:
        for t in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {t}"))
            counts[t] = result.scalar()
    return counts


def truncate_all_data(confirm: bool = False):
    """
    DANGER: Wipe all data from all tables.
    Used to reset simulation. Keeps schema intact.
    """
    if not confirm:
        raise ValueError("Set confirm=True to actually truncate")

    tables_in_order = [
        "risk_scores", "payments", "subscriptions",
        "events", "assessments", "attendance",
        "enrollments", "lessons", "cohorts",
        "user_profiles", "families", "users",
    ]
    # subjects and programs are seed data — keep them

    with engine.begin() as conn:
        for t in tables_in_order:
            conn.execute(text(f"TRUNCATE TABLE {t} CASCADE"))
            log.info(f"Truncated {t}")
    log.info("All transactional tables truncated")


if __name__ == "__main__":
    log.info("Running database healthcheck...")
    if healthcheck():
        log.info("✅ Database connection OK")
        counts = get_table_counts()
        log.info("Current table row counts:")
        for table, count in counts.items():
            log.info(f"  {table:20s} {count:>10,}")
    else:
        log.error("❌ Database connection failed")