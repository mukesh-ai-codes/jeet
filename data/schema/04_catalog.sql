-- ============================================================
-- JEET DATABASE — ACADEMIC CATALOG
-- ============================================================
-- Tables: programs, subjects, cohorts, lessons
-- ============================================================

-- --------------------------------------------------------
-- Table: programs
-- The 3 subscription plans
-- --------------------------------------------------------
CREATE TABLE programs (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slug              VARCHAR(50) UNIQUE NOT NULL,
  name              VARCHAR(80) NOT NULL,
  description       TEXT,
  price_inr         NUMERIC(10,2) NOT NULL,
  duration_months   INTEGER NOT NULL,
  features          JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  display_order     INTEGER NOT NULL DEFAULT 0,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON COLUMN programs.features IS 'JSONB: {live_classes: 5, mentor_calls: 4, ai_tutor: "full", ...}';

-- Seed the 3 plans
INSERT INTO programs (slug, name, description, price_inr, duration_months, features, display_order) VALUES
  ('starter', 'Starter', 'Begin your preparation journey', 8999.00, 3,
   '{"live_classes_per_week": 3, "doubt_sessions": 1, "mentor_calls": 0, "ai_tutor": "basic", "parent_reports": "monthly"}'::jsonb,
   1),
  ('pro', 'Pro', 'Accelerate with full features', 24999.00, 6,
   '{"live_classes_per_week": 5, "doubt_sessions": 2, "mentor_calls": 2, "ai_tutor": "advanced", "parent_reports": "weekly"}'::jsonb,
   2),
  ('mastermind', 'Mastermind', 'Premium 1-on-1 mentorship', 49999.00, 12,
   '{"live_classes_per_week": 5, "doubt_sessions": 3, "mentor_calls": "weekly", "ai_tutor": "premium", "parent_reports": "weekly", "personal_mentor": true}'::jsonb,
   3);

-- --------------------------------------------------------
-- Table: subjects
-- --------------------------------------------------------
CREATE TABLE subjects (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slug         VARCHAR(50) UNIQUE NOT NULL,
  name         VARCHAR(80) NOT NULL,
  exam_types   exam_type[] NOT NULL,  -- A subject can apply to multiple exams
  icon         VARCHAR(50),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO subjects (slug, name, exam_types, icon) VALUES
  ('physics',     'Physics',     ARRAY['jee_main', 'jee_advanced', 'neet_ug']::exam_type[], 'atom'),
  ('chemistry',   'Chemistry',   ARRAY['jee_main', 'jee_advanced', 'neet_ug']::exam_type[], 'flask'),
  ('mathematics', 'Mathematics', ARRAY['jee_main', 'jee_advanced']::exam_type[],            'calculator'),
  ('biology',     'Biology',     ARRAY['neet_ug']::exam_type[],                             'dna');

-- --------------------------------------------------------
-- Table: cohorts
-- Batches of students starting together (e.g., "JEE 2027 — Batch A")
-- --------------------------------------------------------
CREATE TABLE cohorts (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name             VARCHAR(80) NOT NULL,
  program_id       UUID NOT NULL REFERENCES programs(id),
  mentor_user_id   UUID REFERENCES users(id),  -- Assigned mentor
  start_date       DATE NOT NULL,
  end_date         DATE NOT NULL,
  max_students     INTEGER NOT NULL DEFAULT 50,
  current_students INTEGER NOT NULL DEFAULT 0,
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_cohort_dates CHECK (end_date > start_date)
);

-- --------------------------------------------------------
-- Table: lessons
-- Individual class content (videos, notes)
-- --------------------------------------------------------
CREATE TABLE lessons (
  id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  subject_id         UUID NOT NULL REFERENCES subjects(id),
  chapter            VARCHAR(120) NOT NULL,
  title              VARCHAR(200) NOT NULL,
  description        TEXT,
  video_url          TEXT,
  notes_url          TEXT,
  duration_minutes   INTEGER NOT NULL,
  difficulty_level   INTEGER NOT NULL CHECK (difficulty_level BETWEEN 1 AND 5),
  sequence_order     INTEGER NOT NULL,
  is_published       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);