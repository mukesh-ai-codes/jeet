# Day 26 — Data Cleanup Tasks

## Chapter name alignment (assessments vs lessons)

**Discovered:** Day 13 (May 27, 2026), while building the daily plan generator.

**Problem:**
- `assessments.chapter` uses 27 broad concept names (e.g. "Reproduction", "Calculus")
- `lessons.chapter` uses 105 NCERT-granular names (e.g. "Human Reproduction", "Application of Derivatives")
- Only 8 chapter strings overlap between the two tables
- Any join attempting `assessments.chapter = lessons.chapter` silently fails for most rows

**Day 13 workaround:**
Daily plan generator (`GET /api/students/me/daily-plan`) matches on `subject_id`
for SLOT 1 (review) and SLOT 3 (practice) instead of chapter. Loses precision
but works with current seed data. SLOT 2 (learn) unaffected since it walks
lesson sequence by exam type.

**Why this is acceptable for Day 13:**
- Subject-level weakness is still meaningful and demoable
- Demo and pitch story is uncompromised
- Production institutes will plug in their own curriculum (single source of truth)

**Day 26 fix:**
Regenerate seed data with unified chapter taxonomy:
1. Use the 105 NCERT chapter names from `lessons.chapter` as canonical
2. Rewrite `data/scripts/03_seed_behavior.py` to draw assessment chapter
   names from the same NCERT list as the lessons (likely via the existing
   `simulator/curriculum.py`)
3. Re-seed assessments (33,498 rows) — note the rest of the seed depends
   on this so a full reseed is cleaner than a surgical update
4. After reseed, restore the chapter-level matching in the daily plan
   generator's SLOT 1 and SLOT 3 (so messages become "You're 9% on
   Reproduction" instead of "averaging 25% in Biology")
5. Update any other endpoints/queries that joined on chapter — audit:
   - `/api/students/me/recommended-lessons` (likely also affected)
   - `/api/students/me/weak-chapters`
   - Whisper Layer rules (might reference chapter strings)

**Estimated effort:** 2-3 hours.

**Owner:** Day 26 polish pass.
