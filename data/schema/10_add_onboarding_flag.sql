-- Day 12: Add is_onboarded flag to support B2B admin onboarding flow
-- Existing synthetic users are backfilled as onboarded (they have complete profiles)

ALTER TABLE users
ADD COLUMN IF NOT EXISTS is_onboarded BOOLEAN NOT NULL DEFAULT FALSE;

UPDATE users
SET is_onboarded = TRUE
WHERE is_onboarded = FALSE;
