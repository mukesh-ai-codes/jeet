"use client";

/**
 * MentorCard — shows the child's mentor and recent interventions.
 *
 * Two states, both designed with equal care:
 *
 *   EMPTY (no interventions) — the 93% case.
 *     Calm, reassuring. Green check + "On Track" badge.
 *     "[Mentor] hasn't needed to intervene recently. [Child] is
 *      progressing in line with the cohort."
 *
 *   POPULATED (interventions exist) — the at-risk case.
 *     Shows each touchpoint as a structured sentence built from
 *     intervention_type + date + trigger_reason (NOT raw notes, which
 *     are placeholder in the seed). Outcome shown as a colored pill.
 *
 * Why structured-sentence over raw notes: seed notes are auto-generated
 * placeholder text. Real institutes will have real notes; until then the
 * structured framing reads as professional and is demo-safe. When real
 * notes exist (not the placeholder), we show them as a secondary line.
 */

import {
  CheckCircle2,
  Phone,
  MessageSquare,
  Mail,
  HeartHandshake,
  GraduationCap,
  CalendarClock,
} from "lucide-react";
import { format } from "date-fns";
import type { MentorInfo, InterventionSummary } from "@/types";

const PLACEHOLDER_NOTE = "Auto-seeded historical intervention for analytics";

// Map intervention_type → icon + human verb phrase
const TYPE_META: Record<string, { icon: typeof Phone; verb: string }> = {
  mentor_call: { icon: Phone, verb: "called" },
  parent_call: { icon: Phone, verb: "called you about" },
  mentor_message: { icon: MessageSquare, verb: "messaged" },
  parent_email: { icon: Mail, verb: "emailed you about" },
  wellness_check: { icon: HeartHandshake, verb: "checked in on" },
  tutor_session: { icon: GraduationCap, verb: "arranged a session for" },
};

// outcome → label + tone
const OUTCOME_META: Record<string, { label: string; cls: string }> = {
  successful: { label: "Responded well", cls: "bg-emerald-50 text-emerald-700 ring-emerald-200" },
  pending: { label: "Awaiting response", cls: "bg-amber-50 text-amber-700 ring-amber-200" },
  no_response: { label: "No response yet", cls: "bg-orange-50 text-orange-700 ring-orange-200" },
  failed: { label: "Needs follow-up", cls: "bg-red-50 text-red-700 ring-red-200" },
};

function initials(name: string): string {
  return name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
}

export default function MentorCard({
  mentor,
  interventions,
  childFirstName,
}: {
  mentor: MentorInfo | null | undefined;
  interventions: InterventionSummary[];
  childFirstName: string;
}) {
  // No mentor assigned at all — minimal fallback
  if (!mentor) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <h3 className="font-display text-base font-semibold text-slate-900">
          Mentor
        </h3>
        <p className="mt-2 text-sm text-slate-500">
          A mentor will be assigned to {childFirstName} shortly.
        </p>
      </div>
    );
  }

  const hasInterventions = interventions.length > 0;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden">
      {/* Mentor header */}
      <div className="flex items-center gap-3 p-6 pb-4">
        <div className="h-11 w-11 rounded-full bg-indigo-600 text-white text-sm font-bold flex items-center justify-center shrink-0">
          {initials(mentor.full_name)}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs text-slate-500">{childFirstName}&apos;s mentor</p>
          <p className="font-display text-lg font-bold text-slate-900 leading-tight">
            {mentor.full_name}
          </p>
          {mentor.cohort_name && (
            <p className="text-xs text-slate-500 truncate">{mentor.cohort_name}</p>
          )}
        </div>
      </div>

      {hasInterventions ? (
        <PopulatedState
          interventions={interventions}
          mentorName={mentor.full_name}
          childFirstName={childFirstName}
        />
      ) : (
        <EmptyState mentorName={mentor.full_name} childFirstName={childFirstName} />
      )}
    </div>
  );
}

// ---------- EMPTY (healthy) state ----------

function EmptyState({
  mentorName,
  childFirstName,
}: {
  mentorName: string;
  childFirstName: string;
}) {
  return (
    <div className="px-6 pb-6">
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center rounded-full bg-emerald-600 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white">
                On Track
              </span>
            </div>
            <p className="mt-2 text-sm text-emerald-900 leading-relaxed">
              {mentorName.split(" ")[0]}{" "}
              hasn&apos;t needed to intervene recently. {childFirstName}{" "}
              is progressing in line with the cohort.
            </p>
            <p className="mt-2 text-xs text-emerald-700">
              You&apos;ll see a note here the moment your mentor reaches out —
              so you&apos;re never out of the loop.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------- POPULATED (interventions) state ----------

function PopulatedState({
  interventions,
  mentorName,
  childFirstName,
}: {
  interventions: InterventionSummary[];
  mentorName: string;
  childFirstName: string;
}) {
  return (
    <div className="border-t border-slate-100">
      <div className="px-6 py-3 bg-slate-50">
        <p className="text-xs font-semibold text-slate-600">
          Recent check-ins
        </p>
      </div>

      <div className="divide-y divide-slate-100">
        {interventions.map((iv) => (
          <InterventionRow
            key={iv.id}
            iv={iv}
            mentorName={mentorName}
            childFirstName={childFirstName}
          />
        ))}
      </div>
    </div>
  );
}

function InterventionRow({
  iv,
  mentorName,
  childFirstName,
}: {
  iv: InterventionSummary;
  mentorName: string;
  childFirstName: string;
}) {
  const meta = TYPE_META[iv.intervention_type] || {
    icon: MessageSquare,
    verb: "connected with",
  };
  const Icon = meta.icon;

  const outcome = iv.outcome ? OUTCOME_META[iv.outcome] : null;

  const dateStr = format(new Date(iv.created_at), "MMM d");
  const initiatorFirst = iv.initiator_name.split(" ")[0];

  // Build the structured sentence. Use trigger_reason if it reads cleanly.
  const reasonPhrase = iv.trigger_reason
    ? ` regarding ${iv.trigger_reason}`
    : "";

  // Show real notes only if they're not the seed placeholder
  const showNotes =
    iv.notes && iv.notes.trim() && iv.notes.trim() !== PLACEHOLDER_NOTE;

  return (
    <div className="px-6 py-4">
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-indigo-50 p-2 shrink-0">
          <Icon className="h-4 w-4 text-indigo-600" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm text-slate-900 leading-relaxed">
            <span className="font-semibold">{initiatorFirst}</span> {meta.verb}{" "}
            {childFirstName}
            {reasonPhrase} on{" "}
            <span className="font-medium">{dateStr}</span>.
          </p>

          {showNotes && (
            <p className="mt-1 text-xs text-slate-600 italic">
              &ldquo;{iv.notes}&rdquo;
            </p>
          )}

          <div className="mt-2 flex flex-wrap items-center gap-2">
            {outcome && (
              <span
                className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ring-1 ring-inset ${outcome.cls}`}
              >
                {outcome.label}
              </span>
            )}
            {iv.resolved_at && (
              <span className="inline-flex items-center gap-1 text-[10px] text-slate-500">
                <CalendarClock className="h-3 w-3" />
                Followed up {format(new Date(iv.resolved_at), "MMM d")}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
