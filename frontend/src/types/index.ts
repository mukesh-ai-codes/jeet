/**
 * JEET — Shared TypeScript Types
 *
 * Mirrors the Pydantic schemas in the FastAPI backend.
 */

export type UserRole = "student" | "parent" | "mentor" | "admin";

export interface AuthUser {
  user_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
  is_active: boolean;
  email_verified: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export type RiskTier = "urgent" | "critical" | "watch" | "stable" | "lost";

export interface StudentDashboard {
  profile: {
    full_name: string;
    grade: number;
    target_exam: string;
    primary_goal?: string;
    motivation_score?: number;
    weak_subjects: string[];
  };
  enrollment: {
    program_name: string;
    program_slug: string;
    cohort_name?: string;
    mentor_name?: string;
    enrolled_at: string;
    days_active: number;
    status: string;
  };
  engagement: {
    total_logins: number;
    unique_active_days: number;
    days_since_last_login: number;
    active_day_ratio: number;
    sunday_logins: number;
    late_night_logins: number;
  };
  learning: {
    lessons_started: number;
    lessons_completed: number;
    lessons_abandoned: number;
    lesson_completion_rate: number;
    notes_downloaded: number;
    sessions_attended: number;
    sessions_scheduled: number;
    attendance_rate: number;
  };
  assessments: {
    total_assessments: number;
    avg_score_pct: number;
    best_score_pct: number;
    worst_score_pct: number;
    recent_avg_score_pct: number;
    failed_assessments: number;
    strong_assessments: number;
    score_volatility: number;
  };
  recent_assessments: Array<{
    title: string;
    subject: string;
    chapter?: string;
    score: number;
    max_score: number;
    percentage: number;
    submitted_at: string;
  }>;
}

export interface Program {
  id: string;
  slug: string;
  name: string;
  description?: string | null;
  price_inr: number;
  duration_months: number;
  features?: string[] | null;
  is_active: boolean;
}