"use client";

/**
 * StudentDetailDrawer — slide-over panel showing Whisper Layer
 * annotations + suggested intervention + log-intervention form.
 *
 * On successful log:
 *  - Toasts "Intervention logged"
 *  - Calls onLogged() so the parent page can refresh the queue
 *  - Closes
 *
 * This is the screen that makes JEET worth ₹12k/cohort/month —
 * the mentor sees WHY a student is at risk, gets a concrete next
 * action, and a single button records that they acted. The same
 * row instantly becomes visible on the parent's dashboard.
 */

import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
  X, AlertTriangle, Sparkles, Loader2, Send, Phone, MessageSquare, Mail, HeartHandshake, GraduationCap, ChevronDown,
} from "lucide-react";
import type {
  AtRiskStudent,
  StudentWhisperResponse,
  WhisperAnnotation,
} from "@/types";
import { mentorApi, getErrorMessage } from "@/lib/api";
import RiskBadge from "./RiskBadge";

const INTERVENTION_TYPES = [
  { value: "mentor_call",    label: "Phone call",      icon: Phone },
  { value: "mentor_message", label: "WhatsApp / Message", icon: MessageSquare },
  { value: "parent_email",   label: "Email to parent", icon: Mail },
  { value: "wellness_check", label: "Wellness check",  icon: HeartHandshake },
  { value: "tutor_session",  label: "1:1 session",     icon: GraduationCap },
];

export default function StudentDetailDrawer({
  student,
  whisper,
  whisperLoading,
  onClose,
  onLogged,
}: {
  student: AtRiskStudent | null;
  whisper: StudentWhisperResponse | null;
  whisperLoading: boolean;
  onClose: () => void;
  onLogged: () => void;
}) {
  const [interventionType, setInterventionType] = useState("mentor_call");
  const [triggerReason, setTriggerReason] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Pre-fill trigger_reason from Whisper suggestion when it loads
  useEffect(() => {
    if (whisper && whisper.annotations.length > 0) {
      setTriggerReason(whisper.annotations[0].title);
    } else {
      setTriggerReason("");
    }
    setNotes("");
    setInterventionType("mentor_call");
  }, [whisper, student?.student_user_id]);

  if (!student) return null;

  async function handleSubmit() {
    if (!student) return;
    if (!triggerReason.trim()) {
      toast.error("Please enter a reason for this intervention.");
      return;
    }
    setSubmitting(true);
    try {
      await mentorApi.logIntervention({
        student_user_id: student.student_user_id,
        intervention_type: interventionType,
        trigger_reason: triggerReason.trim(),
        notes: notes.trim() || undefined,
      });
      toast.success("Intervention logged.", {
        description: `${student.full_name}'s parent will see this on their dashboard.`,
      });
      onLogged();
      onClose();
    } catch (err) {
      toast.error("Couldn't log that.", { description: getErrorMessage(err) });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-slate-900/30 backdrop-blur-sm"
        onClick={onClose}
      />
      {/* Drawer */}
      <aside className="fixed right-0 top-0 z-50 h-screen w-full max-w-xl bg-white shadow-2xl overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between gap-4">
          <div className="min-w-0">
            <h2 className="font-display text-lg font-bold text-slate-900 truncate">
              {student.full_name}
            </h2>
            <p className="text-xs text-slate-500">
              Class {student.grade} · Risk score {Math.round(student.risk_score)}
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <RiskBadge tier={student.risk_tier} />
            <button
              type="button"
              onClick={onClose}
              className="rounded-full p-1.5 hover:bg-slate-100"
              aria-label="Close"
            >
              <X className="h-4 w-4 text-slate-500" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-6">
          {/* Whisper Layer */}
          <section>
            <h3 className="font-display text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-indigo-600" />
              Why JEET flagged them
            </h3>

            {whisperLoading ? (
              <div className="mt-3 flex items-center gap-2 text-sm text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing signals…
              </div>
            ) : whisper && whisper.annotations.length > 0 ? (
              <div className="mt-3 space-y-3">
                {whisper.annotations.map((a, i) => (
                  <AnnotationCard key={i} annotation={a} />
                ))}
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-500">
                No specific annotations available.
              </p>
            )}
          </section>

          {/* Suggested intervention */}
          {whisper?.suggested_intervention && (
            <section className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-indigo-700">
                Whisper Layer recommends
              </p>
              <p className="mt-1.5 text-sm text-indigo-900 leading-relaxed">
                {whisper.suggested_intervention}
              </p>
            </section>
          )}

          {/* Log intervention form */}
          <section>
            <h3 className="font-display text-sm font-semibold text-slate-900">
              Log an intervention
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              This appears on {student.full_name.split(" ")[0]}&apos;s parent
              dashboard immediately.
            </p>

            <div className="mt-4 space-y-4">
              {/* Type selector */}
              <div>
                <label className="text-xs font-medium text-slate-700">
                  Intervention type
                </label>
                <div className="mt-1.5 grid grid-cols-2 gap-2">
                  {INTERVENTION_TYPES.map((t) => {
                    const Icon = t.icon;
                    const active = t.value === interventionType;
                    return (
                      <button
                        type="button"
                        key={t.value}
                        onClick={() => setInterventionType(t.value)}
                        className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition ${
                          active
                            ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-100"
                            : "border-slate-200 bg-white hover:border-slate-300"
                        }`}
                      >
                        <Icon className={`h-3.5 w-3.5 ${active ? "text-indigo-600" : "text-slate-500"}`} />
                        <span className={active ? "font-semibold text-slate-900" : "text-slate-700"}>
                          {t.label}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Trigger reason */}
              <div>
                <label htmlFor="trigger" className="text-xs font-medium text-slate-700">
                  Trigger reason
                </label>
                <input
                  id="trigger"
                  type="text"
                  value={triggerReason}
                  onChange={(e) => setTriggerReason(e.target.value)}
                  placeholder="e.g. Extended absence"
                  className="mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {/* Notes */}
              <div>
                <label htmlFor="notes" className="text-xs font-medium text-slate-700">
                  Notes (optional)
                </label>
                <textarea
                  id="notes"
                  rows={3}
                  maxLength={500}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="What did you discuss? What's the plan?"
                  className="mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <p className="mt-1 text-[10px] text-slate-500">
                  Visible to the parent. Keep it factual and supportive.
                </p>
              </div>

              {/* Submit */}
              <button
                type="button"
                onClick={handleSubmit}
                disabled={submitting}
                className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:bg-indigo-400 transition"
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Logging…
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Log intervention
                  </>
                )}
              </button>
            </div>
          </section>
        </div>
      </aside>
    </>
  );
}

function AnnotationCard({ annotation }: { annotation: WhisperAnnotation }) {
  const severityClass =
    annotation.severity === "high"
      ? "border-red-200 bg-red-50"
      : annotation.severity === "medium"
      ? "border-amber-200 bg-amber-50"
      : "border-slate-200 bg-slate-50";

  return (
    <div className={`rounded-lg border p-3 ${severityClass}`}>
      <div className="flex items-start gap-2">
        <AlertTriangle
          className={`h-4 w-4 mt-0.5 shrink-0 ${
            annotation.severity === "high" ? "text-red-600" : "text-amber-600"
          }`}
        />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-slate-900">{annotation.title}</p>
          <p className="mt-0.5 text-xs text-slate-700 leading-relaxed">{annotation.detail}</p>
          {annotation.evidence.length > 0 && (
            <details className="mt-1.5 group">
              <summary className="cursor-pointer text-[10px] uppercase tracking-wider text-slate-500 hover:text-slate-700 inline-flex items-center gap-0.5">
                Evidence
                <ChevronDown className="h-3 w-3 group-open:rotate-180 transition" />
              </summary>
              <ul className="mt-1 ml-3 space-y-0.5">
                {annotation.evidence.map((e, i) => (
                  <li key={i} className="text-[10px] text-slate-500 font-mono">
                    {e}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      </div>
    </div>
  );
}
