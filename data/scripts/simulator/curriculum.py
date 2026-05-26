"""
JEET Simulator — Curriculum Engine

Generates a realistic JEE/NEET lesson structure mirroring NCERT chapters.

Output: ~400 lesson records ready for bulk insertion into `lessons` table.

Real-world reference: This curriculum mirrors what platforms like
PhysicsWallah Lakshya, Allen Phoenix, and Unacademy Combat actually teach
in their JEE/NEET online tracks.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict


# =============================================================
# CHAPTER STRUCTURES — REAL NCERT MAPPING
# =============================================================

PHYSICS_CHAPTERS = [
    # Mechanics
    ("Units and Measurements", 4, 2),
    ("Motion in a Straight Line", 5, 2),
    ("Motion in a Plane", 6, 3),
    ("Laws of Motion", 6, 3),
    ("Work, Energy and Power", 5, 3),
    ("System of Particles and Rotational Motion", 6, 4),
    ("Gravitation", 5, 3),
    # Properties of Matter
    ("Mechanical Properties of Solids", 4, 3),
    ("Mechanical Properties of Fluids", 5, 3),
    ("Thermal Properties of Matter", 5, 3),
    # Thermodynamics
    ("Thermodynamics", 6, 4),
    ("Kinetic Theory", 4, 3),
    # Oscillations & Waves
    ("Oscillations", 5, 4),
    ("Waves", 5, 4),
    # Electrostatics
    ("Electric Charges and Fields", 5, 3),
    ("Electrostatic Potential and Capacitance", 6, 4),
    # Current Electricity
    ("Current Electricity", 6, 3),
    # Magnetism
    ("Moving Charges and Magnetism", 5, 4),
    ("Magnetism and Matter", 4, 3),
    # EM Induction & AC
    ("Electromagnetic Induction", 5, 4),
    ("Alternating Current", 5, 4),
    ("Electromagnetic Waves", 4, 3),
    # Optics
    ("Ray Optics and Optical Instruments", 6, 4),
    ("Wave Optics", 5, 4),
    # Modern Physics
    ("Dual Nature of Radiation and Matter", 4, 3),
    ("Atoms", 4, 3),
    ("Nuclei", 4, 4),
    ("Semiconductor Electronics", 5, 4),
]

CHEMISTRY_CHAPTERS = [
    # Physical Chemistry
    ("Some Basic Concepts of Chemistry", 4, 2),
    ("Structure of Atom", 5, 3),
    ("States of Matter", 4, 3),
    ("Thermodynamics", 5, 4),
    ("Equilibrium", 6, 4),
    ("Redox Reactions", 4, 3),
    ("Solutions", 5, 3),
    ("Electrochemistry", 5, 4),
    ("Chemical Kinetics", 5, 4),
    ("Surface Chemistry", 4, 3),
    # Inorganic Chemistry
    ("Classification of Elements and Periodicity", 4, 2),
    ("Chemical Bonding and Molecular Structure", 6, 4),
    ("Hydrogen", 3, 2),
    ("The s-Block Elements", 4, 3),
    ("The p-Block Elements", 6, 4),
    ("The d and f Block Elements", 5, 4),
    ("Coordination Compounds", 5, 4),
    # Organic Chemistry
    ("Organic Chemistry: Basic Principles", 6, 4),
    ("Hydrocarbons", 6, 4),
    ("Haloalkanes and Haloarenes", 5, 4),
    ("Alcohols, Phenols and Ethers", 5, 4),
    ("Aldehydes, Ketones and Carboxylic Acids", 6, 4),
    ("Amines", 4, 4),
    ("Biomolecules", 4, 3),
    ("Polymers", 3, 2),
    ("Chemistry in Everyday Life", 3, 2),
]

MATHEMATICS_CHAPTERS = [
    # Algebra
    ("Sets, Relations and Functions", 5, 3),
    ("Complex Numbers and Quadratic Equations", 5, 3),
    ("Matrices and Determinants", 6, 4),
    ("Permutations and Combinations", 5, 4),
    ("Binomial Theorem", 4, 3),
    ("Sequences and Series", 5, 3),
    # Trigonometry
    ("Trigonometric Functions", 6, 3),
    ("Inverse Trigonometric Functions", 4, 4),
    # Coordinate Geometry
    ("Straight Lines", 4, 3),
    ("Conic Sections", 6, 4),
    ("Three-Dimensional Geometry", 5, 4),
    # Calculus
    ("Limits and Derivatives", 5, 3),
    ("Continuity and Differentiability", 5, 4),
    ("Application of Derivatives", 6, 4),
    ("Integrals", 6, 4),
    ("Application of Integrals", 4, 4),
    ("Differential Equations", 5, 4),
    # Vectors
    ("Vectors", 4, 3),
    # Statistics & Probability
    ("Probability", 5, 4),
    ("Statistics", 3, 2),
    # Linear Programming
    ("Linear Programming", 3, 2),
]

BIOLOGY_CHAPTERS = [
    # Diversity in Living World
    ("The Living World", 3, 1),
    ("Biological Classification", 4, 2),
    ("Plant Kingdom", 5, 3),
    ("Animal Kingdom", 5, 3),
    # Structural Organization
    ("Morphology of Flowering Plants", 5, 3),
    ("Anatomy of Flowering Plants", 4, 3),
    ("Structural Organisation in Animals", 5, 3),
    # Cell Biology
    ("Cell: The Unit of Life", 5, 3),
    ("Biomolecules", 5, 4),
    ("Cell Cycle and Cell Division", 4, 3),
    # Plant Physiology
    ("Photosynthesis in Higher Plants", 5, 4),
    ("Respiration in Plants", 4, 3),
    ("Plant Growth and Development", 4, 3),
    # Human Physiology
    ("Breathing and Exchange of Gases", 4, 3),
    ("Body Fluids and Circulation", 5, 3),
    ("Excretory Products and Their Elimination", 4, 3),
    ("Locomotion and Movement", 4, 3),
    ("Neural Control and Coordination", 5, 4),
    ("Chemical Coordination and Integration", 4, 3),
    # Reproduction
    ("Sexual Reproduction in Flowering Plants", 5, 3),
    ("Human Reproduction", 5, 3),
    ("Reproductive Health", 4, 2),
    # Genetics & Evolution
    ("Principles of Inheritance and Variation", 6, 4),
    ("Molecular Basis of Inheritance", 6, 4),
    ("Evolution", 5, 3),
    # Biology in Human Welfare
    ("Human Health and Disease", 5, 3),
    ("Microbes in Human Welfare", 4, 3),
    # Biotechnology
    ("Biotechnology: Principles and Processes", 4, 4),
    ("Biotechnology and Its Applications", 4, 4),
    # Ecology
    ("Organisms and Populations", 4, 3),
    ("Ecosystem", 5, 3),
    ("Biodiversity and Conservation", 4, 2),
]


# =============================================================
# LESSON FORMAT TEMPLATES
# =============================================================
LESSON_TITLE_TEMPLATES = [
    "Introduction to {chapter}",
    "{chapter} — Core Concepts",
    "{chapter} — Problem Solving",
    "{chapter} — Numerical Practice",
    "{chapter} — Advanced Problems",
    "{chapter} — Quick Revision",
    "{chapter} — PYQ Analysis",
    "{chapter} — Exam Strategy",
]


def _generate_lessons_for_subject(
    rng: random.Random,
    subject_id: str,
    subject_name: str,
    chapter_list: list,
    start_sequence: int = 1,
) -> List[Dict]:
    """Build lesson records for one subject."""
    lessons = []
    sequence = start_sequence

    for chapter_name, num_lessons, default_difficulty in chapter_list:
        for lesson_idx in range(num_lessons):
            title_template = rng.choice(LESSON_TITLE_TEMPLATES)
            title = title_template.format(chapter=chapter_name)

            # Slight difficulty variation per lesson
            difficulty = max(1, min(5, default_difficulty + rng.choice([-1, 0, 0, 0, 1])))

            # Duration: 30-75 minutes typical for online lessons
            duration = rng.randint(35, 75)

            lessons.append({
                "id": str(uuid.uuid4()),
                "subject_id": subject_id,
                "chapter": chapter_name,
                "title": title,
                "description": f"{subject_name} — {chapter_name}. {title_template.format(chapter='this topic').lower()}",
                "video_url": f"https://cdn.jeet.com/lessons/{subject_name.lower()}/{sequence:04d}.mp4",
                "notes_url": f"https://cdn.jeet.com/notes/{subject_name.lower()}/{sequence:04d}.pdf",
                "duration_minutes": duration,
                "difficulty_level": difficulty,
                "sequence_order": sequence,
                "is_published": True,
                "created_at": datetime.now() - timedelta(days=rng.randint(30, 400)),
            })
            sequence += 1

    return lessons


def generate_all_lessons(
    rng: random.Random,
    physics_subject_id: str,
    chemistry_subject_id: str,
    math_subject_id: str,
    biology_subject_id: str,
) -> List[Dict]:
    """Generate the full ~400-lesson curriculum across 4 subjects."""
    all_lessons = []
    seq = 1

    physics_lessons = _generate_lessons_for_subject(
        rng, physics_subject_id, "Physics", PHYSICS_CHAPTERS, seq
    )
    all_lessons.extend(physics_lessons)
    seq += len(physics_lessons)

    chem_lessons = _generate_lessons_for_subject(
        rng, chemistry_subject_id, "Chemistry", CHEMISTRY_CHAPTERS, seq
    )
    all_lessons.extend(chem_lessons)
    seq += len(chem_lessons)

    math_lessons = _generate_lessons_for_subject(
        rng, math_subject_id, "Mathematics", MATHEMATICS_CHAPTERS, seq
    )
    all_lessons.extend(math_lessons)
    seq += len(math_lessons)

    bio_lessons = _generate_lessons_for_subject(
        rng, biology_subject_id, "Biology", BIOLOGY_CHAPTERS, seq
    )
    all_lessons.extend(bio_lessons)

    return all_lessons


# =============================================================
# SANITY TEST
# =============================================================
if __name__ == "__main__":
    rng = random.Random(42)
    fake_ids = {
        "physics":   str(uuid.uuid4()),
        "chemistry": str(uuid.uuid4()),
        "math":      str(uuid.uuid4()),
        "biology":   str(uuid.uuid4()),
    }
    lessons = generate_all_lessons(
        rng, fake_ids["physics"], fake_ids["chemistry"],
        fake_ids["math"], fake_ids["biology"],
    )

    print("=" * 70)
    print(f"CURRICULUM GENERATED — {len(lessons)} total lessons")
    print("=" * 70)

    # Group by subject for summary
    by_subject = {}
    for L in lessons:
        sid = L["subject_id"]
        by_subject.setdefault(sid, []).append(L)

    subject_names = {v: k for k, v in fake_ids.items()}
    for sid, lst in by_subject.items():
        name = subject_names.get(sid, "Unknown")
        chapters = set(L["chapter"] for L in lst)
        total_mins = sum(L["duration_minutes"] for L in lst)
        avg_diff = sum(L["difficulty_level"] for L in lst) / len(lst)
        print(f"  {name.upper():12s}  {len(lst):3d} lessons  {len(chapters):2d} chapters  "
              f"{total_mins/60:5.1f}h total  avg difficulty: {avg_diff:.1f}/5")

    print()
    print("Sample lessons:")
    for L in lessons[:5]:
        print(f"  [{L['sequence_order']:3d}] {L['chapter']:40s} → {L['title']}")
        print(f"        ⏱  {L['duration_minutes']} min · difficulty {L['difficulty_level']}/5")