-- ============================================================
-- JEET DATABASE — IDENTITY & ACCESS
-- ============================================================
-- Tables: users, families, user_profiles
-- This is the foundation. Everything else references users.
-- ============================================================

-- --------------------------------------------------------
-- Table: users
-- The single source of truth for anyone with an account
-- --------------------------------------------------------
CREATE TABLE users (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email           CITEXT UNIQUE NOT NULL,
  phone           VARCHAR(15) UNIQUE,
  password_hash   TEXT NOT NULL,
  full_name       VARCHAR(120) NOT NULL,
  role            user_role NOT NULL,
  avatar_url      TEXT,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  email_verified  BOOLEAN NOT NULL DEFAULT FALSE,
  phone_verified  BOOLEAN NOT NULL DEFAULT FALSE,
  last_login_at   TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE users IS 'All platform users — students, parents, mentors, admins';
COMMENT ON COLUMN users.password_hash IS 'bcrypt hash — NEVER store plain passwords';

-- --------------------------------------------------------
-- Table: families
-- Links parents to their children (many-to-many)
-- --------------------------------------------------------
CREATE TABLE families (
  id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  parent_user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  student_user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  relationship       VARCHAR(20) NOT NULL DEFAULT 'guardian',
  is_primary_payer   BOOLEAN NOT NULL DEFAULT TRUE,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Same parent can't link to same student twice
  CONSTRAINT unique_family_link UNIQUE (parent_user_id, student_user_id),

  -- Sanity: roles must be correct
  CONSTRAINT chk_parent_role CHECK (parent_user_id != student_user_id)
);

COMMENT ON TABLE families IS 'Parent-Student relationships. One parent can have multiple children.';

-- --------------------------------------------------------
-- Table: user_profiles
-- Extended onboarding data (the 8-12 question answers)
-- Separated from users table to keep auth queries fast
-- --------------------------------------------------------
CREATE TABLE user_profiles (
  user_id              UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,

  -- Academic context
  grade                INTEGER CHECK (grade BETWEEN 9 AND 12),
  target_exam          exam_type,
  current_score_band   VARCHAR(20),  -- e.g., '60-70%', '70-80%'

  -- Learning preferences (from onboarding)
  weak_subjects        TEXT[],        -- ['Physics', 'Mathematics']
  daily_study_hours    NUMERIC(3,1),  -- e.g., 2.5
  learning_style       VARCHAR(30),   -- 'video' | 'reading' | 'practice' | 'discussion'
  support_preference   VARCHAR(30),   -- '1-on-1' | 'group' | 'self-study'

  -- Psychological signals
  self_rated_ability   VARCHAR(20),   -- 'excellent' | 'good' | 'average' | 'weak'
  reported_challenges  TEXT[],        -- ['exam_fear', 'time_management']
  primary_goal         TEXT,          -- 'IIT-Bombay', 'AIIMS-Delhi'
  motivation_score     INTEGER CHECK (motivation_score BETWEEN 1 AND 10),

  -- Parent preferences
  update_frequency     VARCHAR(20),   -- 'daily' | 'weekly' | 'monthly'
  additional_concerns  TEXT,          -- Free-text seed for NLP sentiment baseline

  -- Onboarding completeness (analytics)
  onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
  completion_percent   INTEGER NOT NULL DEFAULT 0 CHECK (completion_percent BETWEEN 0 AND 100),

  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE user_profiles IS 'Profile depth from onboarding. Feeds the Sentinel ML model.';