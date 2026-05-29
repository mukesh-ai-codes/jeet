"use client";

/**
 * AdminWizard — one-question-at-a-time onboarding for institute admins.
 *
 * Flow:
 *   8 questions, one per screen, with a progress bar and Back / Next controls.
 *   Final screen is a Review + Finish.
 *
 *   - Enter key advances on text and radio questions (where it doesn't
 *     conflict with multi-line input)
 *   - Per-question zod validation prevents Next until the current question
 *     is valid
 *   - Slide-in / slide-out animation between questions
 *
 * On Finish:
 *   - POST /api/onboarding/admin/configure
 *   - POST /api/auth/complete-onboarding
 *   - Redirect to /admin
 */

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import {
  Loader2,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useAuth } from "@/hooks/useAuth";
import {
  onboardingApi,
  getErrorMessage,
  type AdminConfigurePayload,
} from "@/lib/api";

// =====================================================
// Option data
// =====================================================

const SIZE_OPTIONS = [
  { value: "1-2",   label: "1–2 cohorts",   hint: "Just getting started" },
  { value: "3-5",   label: "3–5 cohorts",   hint: "Single-city operation" },
  { value: "6-15",  label: "6–15 cohorts",  hint: "Multi-cohort campus" },
  { value: "16-50", label: "16–50 cohorts", hint: "Multi-city chain" },
  { value: "50+",   label: "50+ cohorts",   hint: "Large-scale chain" },
] as const;

const EXAM_OPTIONS = [
  { value: "JEE Main", label: "JEE (Main)" },
  { value: "JEE Advanced", label: "JEE (Advanced)" },
  { value: "NEET", label: "NEET" },
  { value: "Foundation", label: "Foundation (Class 8–10)" },
  { value: "Other", label: "Other" },
] as const;

const REVIEW_TOOL_OPTIONS = [
  { value: "spreadsheets",        label: "Excel / Google Sheets",  hint: "Most common starting point" },
  { value: "whatsapp",            label: "WhatsApp groups",         hint: "Mentor chats with parents" },
  { value: "lms",                 label: "Our LMS already has this", hint: "Built-in dashboards" },
  { value: "nothing_structured",  label: "Nothing structured yet",  hint: "Tracking is informal" },
] as const;

const PAIN_OPTIONS = [
  { value: "silent_dropouts", label: "Silent dropouts",   hint: "Students go quiet before they leave" },
  { value: "low_engagement",  label: "Low engagement",    hint: "Attendance and completion sinking" },
  { value: "parent_anxiety",  label: "Parent anxiety",    hint: "Calls about \"is my child OK?\"" },
  { value: "mentor_overload", label: "Mentor overload",   hint: "Mentors don't know where to focus" },
  { value: "revenue_leakage", label: "Revenue leakage",   hint: "Fee defaults and renewals slipping" },
] as const;

const GO_LIVE_OPTIONS = [
  { value: "this_week",  label: "This week",  hint: "Ready to roll" },
  { value: "this_month", label: "This month", hint: "Within 30 days" },
  { value: "exploring",  label: "Just exploring", hint: "Evaluating options" },
] as const;

// =====================================================
// Form state
// =====================================================

type WizardData = {
  institute_name: string;
  institute_size: AdminConfigurePayload["institute_size"] | "";
  primary_exams: AdminConfigurePayload["primary_exams"];
  cohort_count: number | "";
  mentor_count: number | "";
  review_tool_today: AdminConfigurePayload["review_tool_today"] | "";
  biggest_pain: AdminConfigurePayload["biggest_pain"] | "";
  go_live_window: AdminConfigurePayload["go_live_window"] | "";
  notes: string;
};

const INITIAL_DATA: WizardData = {
  institute_name: "",
  institute_size: "",
  primary_exams: [],
  cohort_count: "",
  mentor_count: "",
  review_tool_today: "",
  biggest_pain: "",
  go_live_window: "",
  notes: "",
};

// Per-question validators
const validators = {
  institute_name: (v: string) =>
    v.trim().length < 2 ? "Institute name needs at least 2 characters" : null,
  institute_size: (v: string) =>
    !v ? "Pick a size to continue" : null,
  primary_exams: (v: string[]) =>
    v.length === 0 ? "Pick at least one exam focus" : null,
  cohort_count: (v: number | "") =>
    v === "" || v < 0 ? "Enter the number of cohorts (0 or more)" : null,
  mentor_count: (v: number | "") =>
    v === "" || v < 0 ? "Enter the number of mentors (0 or more)" : null,
  review_tool_today: (v: string) =>
    !v ? "Pick the closest match" : null,
  biggest_pain: (v: string) =>
    !v ? "Pick your biggest pain right now" : null,
  go_live_window: (v: string) =>
    !v ? "Pick a timeline" : null,
};

// =====================================================
// Component
// =====================================================

const TOTAL_STEPS = 9; // 8 questions + 1 review

export default function AdminWizard() {
  const router = useRouter();
  const { user, completeOnboarding } = useAuth();

  const [step, setStep] = useState(1);
  const [data, setData] = useState<WizardData>(INITIAL_DATA);
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [animatingIn, setAnimatingIn] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Re-trigger fade-in animation on step change
  useEffect(() => {
    setAnimatingIn(true);
    const t = setTimeout(() => setAnimatingIn(false), 40);
    return () => clearTimeout(t);
  }, [step]);

  // Auto-focus the container so Enter / Esc work right away
  useEffect(() => {
    containerRef.current?.focus();
  }, [step]);

  function update<K extends keyof WizardData>(key: K, value: WizardData[K]) {
    setData((d) => ({ ...d, [key]: value }));
    setFieldError(null);
  }

  function validateCurrent(): boolean {
    let err: string | null = null;
    switch (step) {
      case 1: err = validators.institute_name(data.institute_name); break;
      case 2: err = validators.institute_size(data.institute_size); break;
      case 3: err = validators.primary_exams(data.primary_exams); break;
      case 4: err = validators.cohort_count(data.cohort_count); break;
      case 5: err = validators.mentor_count(data.mentor_count); break;
      case 6: err = validators.review_tool_today(data.review_tool_today); break;
      case 7: err = validators.biggest_pain(data.biggest_pain); break;
      case 8: err = validators.go_live_window(data.go_live_window); break;
      default: err = null;
    }
    setFieldError(err);
    return err === null;
  }

  function next() {
    if (!validateCurrent()) return;
    setStep((s) => Math.min(s + 1, TOTAL_STEPS));
  }

  function back() {
    setFieldError(null);
    setStep((s) => Math.max(s - 1, 1));
  }

  async function finish() {
    setSubmitError(null);
    setIsSubmitting(true);

    try {
      const payload: AdminConfigurePayload = {
        institute_name: data.institute_name.trim(),
        institute_size: data.institute_size as AdminConfigurePayload["institute_size"],
        primary_exams: data.primary_exams,
        cohort_count: Number(data.cohort_count || 0),
        mentor_count: Number(data.mentor_count || 0),
        review_tool_today: data.review_tool_today as AdminConfigurePayload["review_tool_today"],
        biggest_pain: data.biggest_pain as AdminConfigurePayload["biggest_pain"],
        go_live_window: data.go_live_window as AdminConfigurePayload["go_live_window"],
        notes: data.notes.trim() || undefined,
      };

      await onboardingApi.configureAdmin(payload);
      await completeOnboarding();
      router.replace("/admin");
    } catch (err) {
      setSubmitError(getErrorMessage(err));
      setIsSubmitting(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent) {
    // Allow Enter to advance on most steps; not on textarea (step 9 notes)
    if (e.key === "Enter" && !e.shiftKey) {
      const target = e.target as HTMLElement;
      const isTextarea = target.tagName === "TEXTAREA";
      if (!isTextarea) {
        e.preventDefault();
        if (step === TOTAL_STEPS) {
          finish();
        } else {
          next();
        }
      }
    }
  }

  const progressPct = ((step - 1) / (TOTAL_STEPS - 1)) * 100;

  return (
    <div
      ref={containerRef}
      tabIndex={-1}
      onKeyDown={onKeyDown}
      className="outline-none"
    >
      {/* Progress bar */}
      <div className="mb-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-600">
            {step === TOTAL_STEPS ? "Review" : `Question ${step} of 8`}
          </span>
          <span className="text-xs text-slate-500">
            Press Enter to continue
          </span>
        </div>
        <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-600 transition-all duration-300 ease-out"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Question card */}
      <div
        className={`transition-opacity duration-200 ${
          animatingIn ? "opacity-0" : "opacity-100"
        }`}
      >
        {step === 1 && (
          <Question title="What's the name of your institute?" subtitle="This becomes the label on your JEET workspace.">
            <Input
              autoFocus
              value={data.institute_name}
              onChange={(e) => update("institute_name", e.target.value)}
              placeholder="e.g. Delhi Toppers Academy"
              className="h-12 text-base"
            />
          </Question>
        )}

        {step === 2 && (
          <Question title="How many cohorts do you run today?" subtitle="A rough range is fine — we'll size your trial accordingly.">
            <OptionGrid
              options={SIZE_OPTIONS}
              value={data.institute_size}
              onChange={(v) => update("institute_size", v as WizardData["institute_size"])}
              columns={1}
            />
          </Question>
        )}

        {step === 3 && (
          <Question title="Which exams do you prepare students for?" subtitle="Pick all that apply. Drives the AI tutor's content focus.">
            <MultiOptionGrid
              options={EXAM_OPTIONS}
              value={data.primary_exams}
              onChange={(v) => update("primary_exams", v as WizardData["primary_exams"])}
            />
          </Question>
        )}

        {step === 4 && (
          <Question title="How many active cohorts do you have?" subtitle="An exact count if you can — used for your retention baseline.">
            <Input
              autoFocus
              type="number"
              min={0}
              max={10000}
              value={data.cohort_count}
              onChange={(e) =>
                update(
                  "cohort_count",
                  e.target.value === "" ? "" : Number(e.target.value)
                )
              }
              placeholder="e.g. 8"
              className="h-12 text-base max-w-xs"
            />
          </Question>
        )}

        {step === 5 && (
          <Question title="How many mentors do you have today?" subtitle="The folks who'll use the Coach Console day-to-day.">
            <Input
              autoFocus
              type="number"
              min={0}
              max={10000}
              value={data.mentor_count}
              onChange={(e) =>
                update(
                  "mentor_count",
                  e.target.value === "" ? "" : Number(e.target.value)
                )
              }
              placeholder="e.g. 12"
              className="h-12 text-base max-w-xs"
            />
          </Question>
        )}

        {step === 6 && (
          <Question title="Where do mentors review students today?" subtitle="So we know what JEET is replacing or sitting alongside.">
            <OptionGrid
              options={REVIEW_TOOL_OPTIONS}
              value={data.review_tool_today}
              onChange={(v) => update("review_tool_today", v as WizardData["review_tool_today"])}
              columns={1}
            />
          </Question>
        )}

        {step === 7 && (
          <Question title="What's your biggest churn pain right now?" subtitle="JEET will surface the module that fixes this first.">
            <OptionGrid
              options={PAIN_OPTIONS}
              value={data.biggest_pain}
              onChange={(v) => update("biggest_pain", v as WizardData["biggest_pain"])}
              columns={1}
            />
          </Question>
        )}

        {step === 8 && (
          <Question title="When do you want to go live with JEET?" subtitle="Tells our success team how to prioritize your onboarding.">
            <OptionGrid
              options={GO_LIVE_OPTIONS}
              value={data.go_live_window}
              onChange={(v) => update("go_live_window", v as WizardData["go_live_window"])}
              columns={1}
            />
          </Question>
        )}

        {step === TOTAL_STEPS && (
          <ReviewScreen
            data={data}
            onEdit={(targetStep) => setStep(targetStep)}
            onNotesChange={(v) => update("notes", v)}
          />
        )}
      </div>

      {/* Inline error for current question */}
      {fieldError && (
        <div className="mt-6 flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
          <span>{fieldError}</span>
        </div>
      )}

      {/* Submit error (only on final step) */}
      {submitError && (
        <div className="mt-6 flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
          <span>{submitError}</span>
        </div>
      )}

      {/* Navigation */}
      <div className="mt-10 flex items-center justify-between gap-4">
        <Button
          type="button"
          variant="ghost"
          onClick={back}
          disabled={step === 1 || isSubmitting}
          className="text-slate-600"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>

        {step < TOTAL_STEPS ? (
          <Button
            type="button"
            onClick={next}
            size="lg"
            className="bg-indigo-600 hover:bg-indigo-700"
          >
            Continue
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        ) : (
          <Button
            type="button"
            onClick={finish}
            disabled={isSubmitting}
            size="lg"
            className="bg-indigo-600 hover:bg-indigo-700"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Activating workspace…
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Finish setup
              </>
            )}
          </Button>
        )}
      </div>

      {/* Footer hint */}
      <p className="mt-6 text-center text-xs text-slate-500">
        Hi {user?.full_name?.split(" ")[0] || "there"} — you can update any of
        this later in Settings.
      </p>
    </div>
  );
}

// =====================================================
// Sub-components
// =====================================================

function Question({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h2 className="font-display text-2xl md:text-3xl font-bold text-slate-900 leading-tight">
        {title}
      </h2>
      <p className="mt-2 text-slate-600">{subtitle}</p>
      <div className="mt-8">{children}</div>
    </div>
  );
}

type OptionType = {
  readonly value: string;
  readonly label: string;
  readonly hint?: string;
};

function OptionGrid({
  options,
  value,
  onChange,
  columns,
}: {
  options: readonly OptionType[];
  value: string;
  onChange: (v: string) => void;
  columns: 1 | 2;
}) {
  const grid = columns === 1 ? "grid-cols-1" : "grid-cols-1 md:grid-cols-2";

  return (
    <div className={`grid ${grid} gap-2`}>
      {options.map((opt) => {
        const checked = value === opt.value;
        return (
          <button
            type="button"
            key={opt.value}
            onClick={() => onChange(opt.value)}
            className={`text-left rounded-xl border px-4 py-3.5 transition ${
              checked
                ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-100"
                : "border-slate-200 bg-white hover:border-slate-300"
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`h-4 w-4 rounded-full border-2 flex items-center justify-center shrink-0 ${
                  checked ? "border-indigo-600" : "border-slate-300"
                }`}
              >
                {checked && <div className="h-1.5 w-1.5 rounded-full bg-indigo-600" />}
              </div>
              <div>
                <div
                  className={`text-sm ${
                    checked ? "font-semibold text-slate-900" : "text-slate-800"
                  }`}
                >
                  {opt.label}
                </div>
                {opt.hint && (
                  <div className="text-xs text-slate-500 mt-0.5">{opt.hint}</div>
                )}
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}

function MultiOptionGrid({
  options,
  value,
  onChange,
}: {
  options: readonly OptionType[];
  value: string[];
  onChange: (v: string[]) => void;
}) {
  function toggle(v: string) {
    if (value.includes(v)) onChange(value.filter((x) => x !== v));
    else onChange([...value, v]);
  }

  return (
    <div className="grid grid-cols-2 gap-2">
      {options.map((opt) => {
        const checked = value.includes(opt.value);
        return (
          <button
            type="button"
            key={opt.value}
            onClick={() => toggle(opt.value)}
            className={`rounded-xl border px-4 py-3.5 text-left transition ${
              checked
                ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-100"
                : "border-slate-200 bg-white hover:border-slate-300"
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`h-5 w-5 rounded border-2 flex items-center justify-center shrink-0 ${
                  checked ? "border-indigo-600 bg-indigo-600" : "border-slate-300"
                }`}
              >
                {checked && <CheckCircle2 className="h-3.5 w-3.5 text-white" />}
              </div>
              <span
                className={`text-sm ${
                  checked ? "font-semibold text-slate-900" : "text-slate-800"
                }`}
              >
                {opt.label}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}

// =====================================================
// Review screen
// =====================================================

function ReviewScreen({
  data,
  onEdit,
  onNotesChange,
}: {
  data: WizardData;
  onEdit: (step: number) => void;
  onNotesChange: (v: string) => void;
}) {
  const rows: Array<{ step: number; label: string; value: string }> = [
    { step: 1, label: "Institute",       value: data.institute_name },
    { step: 2, label: "Size",            value: SIZE_OPTIONS.find((o) => o.value === data.institute_size)?.label || "—" },
    { step: 3, label: "Exam focus",      value: data.primary_exams.join(", ") || "—" },
    { step: 4, label: "Active cohorts",  value: String(data.cohort_count || 0) },
    { step: 5, label: "Active mentors",  value: String(data.mentor_count || 0) },
    { step: 6, label: "Review tool",     value: REVIEW_TOOL_OPTIONS.find((o) => o.value === data.review_tool_today)?.label || "—" },
    { step: 7, label: "Biggest pain",    value: PAIN_OPTIONS.find((o) => o.value === data.biggest_pain)?.label || "—" },
    { step: 8, label: "Go-live window",  value: GO_LIVE_OPTIONS.find((o) => o.value === data.go_live_window)?.label || "—" },
  ];

  return (
    <div>
      <h2 className="font-display text-2xl md:text-3xl font-bold text-slate-900 leading-tight">
        One last look.
      </h2>
      <p className="mt-2 text-slate-600">
        Edit anything below before activating your workspace.
      </p>

      <div className="mt-8 divide-y divide-slate-200 border border-slate-200 rounded-xl bg-white">
        {rows.map((r) => (
          <div key={r.step} className="flex items-center justify-between gap-4 px-4 py-3">
            <div className="min-w-0">
              <div className="text-xs font-semibold text-slate-500">{r.label}</div>
              <div className="text-sm text-slate-900 truncate">{r.value}</div>
            </div>
            <button
              type="button"
              onClick={() => onEdit(r.step)}
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 shrink-0"
            >
              Edit
            </button>
          </div>
        ))}
      </div>

      <div className="mt-6">
        <label htmlFor="notes" className="text-sm font-medium text-slate-900">
          Anything else we should know? (optional)
        </label>
        <textarea
          id="notes"
          rows={3}
          maxLength={500}
          value={data.notes}
          onChange={(e) => onNotesChange(e.target.value)}
          placeholder="e.g. We're piloting with one cohort first, expanding in Q3."
          className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>
  );
}
