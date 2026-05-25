-- ============================================================
-- JEET DATABASE — ENUMS (Predefined Lists)
-- ============================================================
-- Enums = restricted text values. Database rejects invalid values.
-- Better than free text — prevents typos, faster, enforces consistency.
-- ============================================================

-- User roles in the platform
CREATE TYPE user_role AS ENUM (
  'student',
  'parent',
  'mentor',
  'admin'
);

-- Target competitive exams
CREATE TYPE exam_type AS ENUM (
  'jee_main',
  'jee_advanced',
  'neet_ug',
  'foundation',
  'board'
);

-- Subscription lifecycle states
CREATE TYPE subscription_status AS ENUM (
  'trial',
  'active',
  'paused',
  'expired',
  'cancelled',
  'churned'
);

-- Payment states (matches Razorpay's status model)
CREATE TYPE payment_status AS ENUM (
  'created',
  'authorized',
  'captured',
  'refunded',
  'failed'
);

-- Risk tiers from the Sentinel Engine
CREATE TYPE risk_tier AS ENUM (
  'stable',     -- < 25% churn probability
  'watch',      -- 25-50%
  'critical',   -- 50-75%
  'urgent'      -- > 75%
);

-- Intervention types triggered by Pulse
CREATE TYPE intervention_type AS ENUM (
  'in_app_nudge',
  'parent_whatsapp',
  'parent_email',
  'mentor_call_scheduled',
  'ai_tutor_revision_pack',
  'discount_offer'
);