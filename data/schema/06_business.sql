-- ============================================================
-- JEET DATABASE — BUSINESS & PAYMENTS
-- ============================================================
-- Tables: subscriptions, payments
-- ============================================================

-- --------------------------------------------------------
-- Table: subscriptions
-- Active subscription state per student
-- --------------------------------------------------------
CREATE TABLE subscriptions (
  id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  payer_user_id        UUID NOT NULL REFERENCES users(id),
  program_id           UUID NOT NULL REFERENCES programs(id),
  enrollment_id        UUID REFERENCES enrollments(id),

  start_date           DATE NOT NULL,
  end_date             DATE NOT NULL,
  status               subscription_status NOT NULL DEFAULT 'trial',

  -- Renewal intelligence
  auto_renew           BOOLEAN NOT NULL DEFAULT FALSE,
  renewal_attempts     INTEGER NOT NULL DEFAULT 0,
  cancelled_at         TIMESTAMPTZ,
  cancellation_reason  TEXT,

  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT chk_subscription_dates CHECK (end_date > start_date)
);

-- --------------------------------------------------------
-- Table: payments
-- Transaction ledger (matches Razorpay model)
-- --------------------------------------------------------
CREATE TABLE payments (
  id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  subscription_id       UUID NOT NULL REFERENCES subscriptions(id),
  payer_user_id         UUID NOT NULL REFERENCES users(id),

  amount_inr            NUMERIC(10,2) NOT NULL,
  currency              VARCHAR(3) NOT NULL DEFAULT 'INR',
  status                payment_status NOT NULL DEFAULT 'created',
  payment_method        VARCHAR(50),  -- 'upi' | 'card' | 'netbanking'

  -- Razorpay integration fields (for production payment gateway)
  razorpay_order_id     VARCHAR(100),
  razorpay_payment_id   VARCHAR(100),
  razorpay_signature    TEXT,

  -- Idempotency: prevents double-charging
  idempotency_key       VARCHAR(100) UNIQUE,

  initiated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  paid_at               TIMESTAMPTZ,
  failed_at             TIMESTAMPTZ,
  failure_reason        TEXT,

  -- Refund tracking
  refunded_amount_inr   NUMERIC(10,2) DEFAULT 0,
  refunded_at           TIMESTAMPTZ
);

COMMENT ON COLUMN payments.idempotency_key IS 'Stripe-style idempotency. Same key = same payment, never duplicate.';