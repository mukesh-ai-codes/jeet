"""
JEET Simulator — Central Configuration

Loads environment variables and exposes them as Python constants.
This is the single source of truth for all simulation parameters.
"""

import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# --------------------------------------------------------
# Database
# --------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("JEET_DB_HOST", "localhost")
DB_PORT = int(os.getenv("JEET_DB_PORT", 5432))
DB_NAME = os.getenv("JEET_DB_NAME", "jeet_dev")
DB_USER = os.getenv("JEET_DB_USER", "")
DB_PASSWORD = os.getenv("JEET_DB_PASSWORD", "")

# --------------------------------------------------------
# Simulation Scale
# --------------------------------------------------------
NUM_STUDENTS = int(os.getenv("JEET_SIM_STUDENTS", 3000))
NUM_DAYS = int(os.getenv("JEET_SIM_DAYS", 120))
RANDOM_SEED = int(os.getenv("JEET_SIM_SEED", 42))

START_DATE = date.fromisoformat(os.getenv("JEET_SIM_START_DATE", "2026-01-01"))

# --------------------------------------------------------
# Derived Scale Targets
# --------------------------------------------------------
NUM_PARENTS = int(NUM_STUDENTS * 0.85)  # Most students have parent accounts
NUM_MENTORS = max(20, NUM_STUDENTS // 60)  # 1 mentor per ~60 students
NUM_ADMINS = 5
NUM_COHORTS = max(10, NUM_STUDENTS // 50)

# --------------------------------------------------------
# Archetype Distribution
# --------------------------------------------------------
# Sums to ~100% with 5% noise/unclassifiable
STUDENT_ARCHETYPES = {
    "disciplined_topper":        0.08,
    "diligent_struggler":        0.15,
    "unengaged_genius":          0.06,
    "hostel_burnout":            0.12,
    "parent_forced":             0.10,
    "financially_stressed":      0.14,
    "distracted_multitasker":    0.18,
    "repeater":                  0.17,
}

PARENT_ARCHETYPES = {
    "helicopter_monitor":  0.25,
    "hopeful_investor":    0.40,
    "hands_off_trustee":   0.20,
    "anxious_pressurizer": 0.15,
}

# --------------------------------------------------------
# Indian Context — Cities & Languages
# --------------------------------------------------------
INDIAN_CITIES_TIER_1 = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata"]
INDIAN_CITIES_TIER_2 = [
    "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal", "Patna",
    "Surat", "Vadodara", "Coimbatore", "Vizag", "Bhubaneswar", "Chandigarh",
    "Kochi", "Mysore", "Mangalore", "Madurai", "Trichy", "Salem",
]
INDIAN_CITIES_TIER_3 = [
    "Kota", "Sikar", "Aligarh", "Meerut", "Allahabad", "Varanasi", "Gorakhpur",
    "Jabalpur", "Gwalior", "Ranchi", "Dhanbad", "Jamshedpur", "Bhilai",
    "Raipur", "Bilaspur", "Hubli", "Belgaum", "Tirupati", "Vijayawada",
]
KOTA_HUB_CITIES = ["Kota", "Sikar", "Hyderabad", "Delhi"]  # Coaching hubs

# Realistic city distribution (Tier-2 is the largest JEE/NEET base)
CITY_TIER_DISTRIBUTION = {
    "tier_1": 0.25,
    "tier_2": 0.45,
    "tier_3": 0.30,
}

# --------------------------------------------------------
# Validation
# --------------------------------------------------------
assert NUM_STUDENTS > 0, "NUM_STUDENTS must be positive"
assert NUM_DAYS > 0, "NUM_DAYS must be positive"
assert abs(sum(STUDENT_ARCHETYPES.values()) - 1.0) < 0.01, "Student archetypes must sum to ~1.0"
assert abs(sum(PARENT_ARCHETYPES.values()) - 1.0) < 0.01, "Parent archetypes must sum to ~1.0"


def summary():
    """Print configuration summary."""
    print("=" * 60)
    print("JEET SIMULATOR CONFIGURATION")
    print("=" * 60)
    print(f"  Database:         {DB_NAME} @ {DB_HOST}:{DB_PORT}")
    print(f"  Students:         {NUM_STUDENTS:,}")
    print(f"  Parents:          {NUM_PARENTS:,}")
    print(f"  Mentors:          {NUM_MENTORS}")
    print(f"  Cohorts:          {NUM_COHORTS}")
    print(f"  Simulation days:  {NUM_DAYS}")
    print(f"  Start date:       {START_DATE}")
    print(f"  Random seed:      {RANDOM_SEED}")
    print("=" * 60)


if __name__ == "__main__":
    summary()