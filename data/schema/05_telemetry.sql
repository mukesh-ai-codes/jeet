-- ============================================================
-- JEET DATABASE — LEARNING TELEMETRY
-- ============================================================
-- Tables: enrollments, attendance, assessments, events
-- These tables grow LARGE. Indexed carefully in 08_indexes.sql
-- ============================================================

-- --------------------------------------------------------
-- Table: enrollments
-- Which student is in which program/cohort
-- --------------------------------------------------------
CREATE TABLE enrollments (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  program_id          UUID NOT NULL REFERENCES programs(id),
  cohort_id           UUID REFERENCES cohorts(id),
  enrolled_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ended_at            TIMESTAMPTZ,
  status              subscription_status NOT NULL DEFAULT 'active',
  churn_reason        TEXT,  -- Free text if churned

  CONSTRAINT unique_active_enrollment UNIQUE (student_user_id, program_id, status)
);

-- --------------------------------------------------------
-- Table: attendance
-- Per-session participation logs
-- --------------------------------------------------------
CREATE TABLE attendance (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  enrollment_id       UUID NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
  lesson_id           UUID REFERENCES lessons(id),
  subject_id          UUID NOT NULL REFERENCES subjects(id),
  session_date        DATE NOT NULL,
  joined              BOOLEAN NOT NULL,
  joined_at           TIMESTAMPTZ,
  left_at             TIMESTAMPTZ,
  duration_minutes    INTEGER NOT NULL DEFAULT 0,
  engagement_score    NUMERIC(4,2),  -- 0-100, computed from interactions
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON COLUMN attendance.engagement_score IS 'Composite: chat activity + doubt asks + poll participation';

-- --------------------------------------------------------
-- Table: assessments
-- Quiz/test submissions
-- --------------------------------------------------------
CREATE TABLE assessments (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  subject_id          UUID NOT NULL REFERENCES subjects(id),
  chapter             VARCHAR(120),
  title               VARCHAR(200) NOT NULL,
  score               NUMERIC(6,2) NOT NULL,
  max_score           NUMERIC(6,2) NOT NULL,
  percentage          NUMERIC(5,2) GENERATED ALWAYS AS (score / NULLIF(max_score, 0) * 100) STORED,
  time_taken_minutes  INTEGER,
  difficulty_level    INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
  submitted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON COLUMN assessments.percentage IS 'Auto-computed column — never set manually';

-- --------------------------------------------------------
-- Table: events  ← THE BIG ONE
-- Every interaction. Powers analytics, ML features, recommendations.
-- --------------------------------------------------------
CREATE TABLE events (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  event_type   VARCHAR(80) NOT NULL,
  event_data   JSONB NOT NULL DEFAULT '{}'::jsonb,
  session_id   UUID,  -- Groups events from one login session
  ip_address   INET,
  user_agent   TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE events IS 'Event stream. Examples: login, lesson_started, doubt_asked, quiz_submitted';
COMMENT ON COLUMN events.event_data IS 'Schemaless JSON. Different event_types have different data shapes.';

-- Example event_data shapes (documented here for the team):
-- event_type='lesson_started': {lesson_id: "...", watch_speed: 1.0}
-- event_type='doubt_asked': {lesson_id: "...", question: "...", tutor_response_time_ms: 1200}
-- event_type='quiz_submitted': {assessment_id: "...", score_percentage: 75.5}