"use client";

/**
 * TaraTeaser — promotes the upcoming AI tutor inside the student dashboard.
 *
 * Visible from Day 13 even though Tara doesn't ship until Days 20-23.
 * Tells students (and demo viewers) the AI story aggressively without
 * faking the product.
 */

import Link from "next/link";
import { Sparkles, BookOpen, MessageSquare, Lightbulb } from "lucide-react";

const HIGHLIGHTS = [
  {
    icon: BookOpen,
    text: "RAG-grounded on full NCERT syllabus",
  },
  {
    icon: MessageSquare,
    text: "3 modes — Saathi · Strategist · Guru",
  },
  {
    icon: Lightbulb,
    text: "Indian-context analogies that make hard topics click",
  },
];

export default function TaraTeaser() {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-indigo-200 bg-gradient-to-br from-indigo-600 via-indigo-700 to-indigo-900 text-white">
      {/* Decorative concentric arcs */}
      <svg
        viewBox="0 0 400 400"
        className="absolute -right-20 -top-20 w-80 h-80 opacity-25 pointer-events-none"
        aria-hidden="true"
      >
        <defs>
          <radialGradient id="taraGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#F97316" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#F97316" stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx="200" cy="200" r="180" fill="url(#taraGlow)" />
        <circle cx="200" cy="200" r="160" fill="none" stroke="white" strokeWidth="1.5" strokeOpacity="0.3" />
        <circle cx="200" cy="200" r="120" fill="none" stroke="white" strokeWidth="2" strokeOpacity="0.45" />
        <circle cx="200" cy="200" r="80" fill="none" stroke="white" strokeWidth="2" strokeOpacity="0.7" />
        <circle cx="200" cy="200" r="20" fill="#F97316" />
      </svg>

      <div className="relative z-10 p-6 md:p-8 grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        <div className="md:col-span-2">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold backdrop-blur-sm">
            <Sparkles className="h-3 w-3 text-orange-300" />
            Live now · Agentic AI Tutor
          </div>

          <h2 className="mt-4 font-display text-2xl md:text-3xl font-bold leading-tight">
            Meet Tara — your AI study companion.
          </h2>

          <p className="mt-2 text-sm md:text-base text-indigo-100 leading-relaxed max-w-2xl">
            A RAG-based agentic tutor trained on the full NCERT corpus, with
            three personality modes and frustration-aware mentor handoff.
            Built for the Indian student.
          </p>

          <div className="mt-5 space-y-2">
            {HIGHLIGHTS.map((h, i) => {
              const Icon = h.icon;
              return (
                <div key={i} className="flex items-center gap-2 text-sm text-indigo-100">
                  <Icon className="h-3.5 w-3.5 text-orange-300 shrink-0" />
                  <span>{h.text}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex justify-start md:justify-end">
          <Link
            href="/student/tara"
            className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-indigo-700 shadow-sm transition hover:bg-indigo-50"
          >
            <Sparkles className="h-4 w-4 text-orange-500" />
            Chat with Tara
          </Link>
        </div>
      </div>
    </div>
  );
}
