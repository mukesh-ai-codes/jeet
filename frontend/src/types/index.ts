/**
 * JEET — Shared TypeScript Types
 *
 * Mirrors the Pydantic schemas in the FastAPI backend.
 * When backend schemas change, this file is the single point of update.
 */

// =========================
// Roles & Auth
// =========================

export type UserRole = "student" | "parent" | "mentor" | "admin";

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string | null;
  institute_id: string;
  is_onboarded: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

// =========================
// Risk tiers (mentor / admin views)
// =========================

export type RiskTier = "urgent" | "critical" | "watch" | "stable" | "lost";

// =========================
// Student dashboard
// (Returned from GET /api/students/me/dashboard — Day 13 will consume this)
// =========================

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
  risk_tier: RiskTier;
  risk_score: number;
}

// =========================
// Catalog
// =========================

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


// =========================
// Daily plan (Day 13)
// =========================

export type DailyPlanSlot = "review" | "learn" | "practice";

export interface LessonSummary {
  id: string;
  subject_name: string;
  chapter: string;
  title: string;
  duration_minutes: number;
  difficulty_level: number;
  sequence_order: number;
}

export interface DailyPlanItem {
  slot: DailyPlanSlot;
  label: string;
  reason: string;
  lesson: LessonSummary;
}

export interface DailyPlanResponse {
  student_user_id: string;
  items: DailyPlanItem[];
  generated_at: string;
}

// =========================
// Weak chapters (existing endpoint, type for Day 13)
// =========================

export interface WeakChapter {
  subject_name: string;
  chapter: string;
  quizzes_attempted: number;
  avg_score: number;
  last_attempted_at?: string;
}

export interface WeakChaptersResponse {
  student_user_id: string;
  weak_chapters: WeakChapter[];
}


// =========================
// Streak (Day 13)
// =========================

export interface DailyActivity {
  activity_date: string;
  has_activity: boolean;
}

export interface StreakResponse {
  current_streak: number;
  longest_streak: number;
  total_active_days: number;
  daily_activity: DailyActivity[];
}


// =========================
// Lesson detail + list (Day 13)
// =========================

export interface LessonDetail {
  id: string;
  subject_id: string;
  subject_name: string;
  chapter: string;
  title: string;
  description?: string | null;
  video_url?: string | null;
  notes_url?: string | null;
  duration_minutes: number;
  difficulty_level: number;
  sequence_order: number;
  is_published: boolean;
}

export interface LessonListResponse {
  total: number;
  page: number;
  page_size: number;
  lessons: LessonSummary[];
}


// =========================
// Parent dashboard (Day 14)
// =========================

export interface ChildSummary {
  student_user_id: string;
  full_name: string;
  grade: number;
  target_exam: string;
  program_name: string;
  enrollment_status: string;
  relationship: string;
}

export interface ParentChildrenResponse {
  children: ChildSummary[];
}

export interface WhisperInsight {
  severity: "positive" | "info" | "watch" | "urgent";
  category: "engagement" | "academic" | "wellness" | "financial";
  message: string;
  metric_value?: number | null;
}

export interface MentorInfo {
  full_name: string;
  email?: string | null;
  cohort_name?: string | null;
}

export interface InterventionSummary {
  id: string;
  intervention_type: string;
  notes?: string | null;
  outcome?: string | null;
  trigger_reason?: string | null;
  created_at: string;
  resolved_at?: string | null;
  initiator_name: string;
}

export interface ParentDashboard {
  child_name: string;
  grade: number;
  target_exam: string;
  program_name: string;
  days_active: number;
  enrollment_status: string;
  total_logins: number;
  days_since_last_login: number;
  lesson_completion_rate: number;
  avg_score_pct: number;
  attendance_rate: number;
  insights: WhisperInsight[];
  last_login_at?: string | null;
  mentor?: MentorInfo | null;
  recent_interventions: InterventionSummary[];
}

// =========================
// Mentor — at-risk + whisper (Day 15/19; defined here to harden tsc build)
// =========================

export interface AtRiskStudent {
  student_user_id: string;
  full_name: string;
  grade: number;
  target_exam: string;
  program_slug: string;
  days_since_last_login: number;
  lesson_completion_rate: number;
  avg_score_pct: number;
  attendance_rate: number;
  failed_assessments: number;
  failed_payments: number;
  risk_score: number;
  risk_tier: RiskTier;
  enrollment_status: string;
}

export interface WhisperAnnotation {
  category: "concern" | "positive" | "info";
  severity: "high" | "medium" | "low";
  title: string;
  detail: string;
  evidence: string[];
}

export interface StudentWhisperResponse {
  student_user_id: string;
  full_name: string;
  risk_tier: RiskTier;
  risk_score: number;
  annotations: WhisperAnnotation[];
  suggested_intervention?: string;
  model_reasons?: string[];
}
