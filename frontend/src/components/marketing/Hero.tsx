import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

function HeroIllustration() {
  return (
    <svg
      viewBox="0 0 600 480"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-auto"
      aria-label="JEET signal catches at-risk students in a cohort before they drop out"
    >
      {/* Background ambient gradient */}
      <defs>
        <radialGradient id="bgGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#F1F0FE" />
          <stop offset="100%" stopColor="#FAFAF9" />
        </radialGradient>
        <radialGradient id="signalGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#4F46E5" stopOpacity="0.15" />
          <stop offset="100%" stopColor="#4F46E5" stopOpacity="0" />
        </radialGradient>
      </defs>

      <rect width="600" height="480" fill="url(#bgGlow)" rx="24" />

      {/* ============ LEFT: Cohort BEFORE (mixed states) ============ */}
      <g transform="translate(60, 100)">
        <text
          x="60"
          y="-20"
          textAnchor="middle"
          fontSize="11"
          fontWeight="600"
          fill="#64748B"
          letterSpacing="1"
        >
          COHORT
        </text>

        {/* Row 1 */}
        <circle cx="20" cy="20" r="14" fill="#22C55E" />
        <circle cx="60" cy="20" r="14" fill="#22C55E" />
        <circle cx="100" cy="20" r="14" fill="#F97316" />

        {/* Row 2 */}
        <circle cx="20" cy="60" r="14" fill="#22C55E" />
        <circle cx="60" cy="60" r="14" fill="#F97316" />
        <circle cx="100" cy="60" r="14" fill="#94A3B8" />

        {/* Row 3 */}
        <circle cx="20" cy="100" r="14" fill="#F97316" />
        <circle cx="60" cy="100" r="14" fill="#22C55E" />
        <circle cx="100" cy="100" r="14" fill="#94A3B8" />

        {/* Row 4 */}
        <circle cx="20" cy="140" r="14" fill="#22C55E" />
        <circle cx="60" cy="140" r="14" fill="#94A3B8" />
        <circle cx="100" cy="140" r="14" fill="#F97316" />

        {/* Legend */}
        <g transform="translate(-10, 180)">
          <circle cx="6" cy="6" r="5" fill="#22C55E" />
          <text x="18" y="10" fontSize="10" fill="#475569">Engaged</text>

          <circle cx="6" cy="26" r="5" fill="#F97316" />
          <text x="18" y="30" fontSize="10" fill="#475569">At-risk</text>

          <circle cx="6" cy="46" r="5" fill="#94A3B8" />
          <text x="18" y="50" fontSize="10" fill="#475569">Dropping out</text>
        </g>
      </g>

      {/* ============ CENTER: JEET Signal Wave ============ */}
      <g transform="translate(300, 240)">
        {/* Outer glow */}
        <circle cx="0" cy="0" r="110" fill="url(#signalGlow)" />

        {/* Three concentric arcs — same as Signal Waves logo */}
        <circle
          cx="0"
          cy="0"
          r="90"
          fill="none"
          stroke="#4F46E5"
          strokeWidth="2"
          strokeOpacity="0.3"
        />
        <circle
          cx="0"
          cy="0"
          r="65"
          fill="none"
          stroke="#4F46E5"
          strokeWidth="2.5"
          strokeOpacity="0.55"
        />
        <circle
          cx="0"
          cy="0"
          r="40"
          fill="none"
          stroke="#4F46E5"
          strokeWidth="3"
          strokeOpacity="1"
        />

        {/* Center orange dot — the JEET signal core */}
        <circle cx="0" cy="0" r="14" fill="#F97316" />

        {/* JEET label below center */}
        <text
          x="0"
          y="135"
          textAnchor="middle"
          fontSize="12"
          fontWeight="700"
          fill="#1E1B4B"
          letterSpacing="2"
        >
          JEET
        </text>
        <text
          x="0"
          y="152"
          textAnchor="middle"
          fontSize="9"
          fill="#64748B"
          letterSpacing="1"
        >
          Retention OS
        </text>
      </g>

      {/* Signal capturing the at-risk dots — subtle connecting strokes */}
      <g stroke="#F97316" strokeWidth="1.2" strokeOpacity="0.4" fill="none" strokeDasharray="3,3">
        <path d="M 160 120 Q 230 200, 260 240" />
        <path d="M 160 160 Q 220 210, 260 240" />
        <path d="M 160 200 Q 220 220, 260 240" />
      </g>

      {/* ============ RIGHT: Cohort AFTER (mostly green + saved) ============ */}
      <g transform="translate(440, 100)">
        <text
          x="60"
          y="-20"
          textAnchor="middle"
          fontSize="11"
          fontWeight="600"
          fill="#64748B"
          letterSpacing="1"
        >
          14 DAYS LATER
        </text>

        {/* Row 1 */}
        <circle cx="20" cy="20" r="14" fill="#22C55E" />
        <circle cx="60" cy="20" r="14" fill="#22C55E" />
        <circle cx="100" cy="20" r="14" fill="#22C55E" />

        {/* Row 2 */}
        <circle cx="20" cy="60" r="14" fill="#22C55E" />
        <circle cx="60" cy="60" r="14" fill="#22C55E" />
        <circle cx="100" cy="60" r="14" fill="#22C55E" />

        {/* Row 3 */}
        <circle cx="20" cy="100" r="14" fill="#22C55E" />
        <circle cx="60" cy="100" r="14" fill="#22C55E" />
        <circle cx="100" cy="100" r="14" fill="#F97316" />

        {/* Row 4 */}
        <circle cx="20" cy="140" r="14" fill="#22C55E" />
        <circle cx="60" cy="140" r="14" fill="#22C55E" />
        <circle cx="100" cy="140" r="14" fill="#22C55E" />

        {/* Retention badge */}
        <g transform="translate(-10, 185)">
          <rect
            x="0"
            y="0"
            width="140"
            height="32"
            rx="16"
            fill="#22C55E"
            fillOpacity="0.1"
            stroke="#22C55E"
            strokeWidth="1"
          />
          <text x="70" y="20" textAnchor="middle" fontSize="12" fontWeight="700" fill="#15803D">
            +12% retention
          </text>
        </g>
      </g>
    </svg>
  );
}

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-white">
      <div className="mx-auto max-w-7xl px-6 py-20 md:py-28">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* LEFT: Copy */}
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">
              <span className="h-1.5 w-1.5 rounded-full bg-orange-500 animate-pulse" />
              Retention OS for coaching institutes
            </div>

            <h1 className="mt-6 font-display text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 leading-[1.1]">
              Stop dropouts <span className="text-indigo-600">before</span> they
              start.
            </h1>

            <p className="mt-6 text-lg text-slate-600 max-w-xl leading-relaxed">
              JEET catches at-risk students 14 days before they disengage —
              and gives your mentors the exact playbook to save them. Built for
              India's JEE and NEET coaching institutes.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row gap-3">
              <Button size="lg" className="bg-indigo-600 hover:bg-indigo-700">
                Book a demo
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button size="lg" variant="outline">
                See how it works
              </Button>
            </div>

            <p className="mt-4 text-xs text-slate-500">
              Free 30-day pilot. No card required. Setup in under a week.
            </p>
          </div>

          {/* RIGHT: Illustration */}
          <div className="relative">
            <HeroIllustration />
          </div>
        </div>
      </div>
    </section>
  );
}
