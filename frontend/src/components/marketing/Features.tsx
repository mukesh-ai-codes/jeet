import {
  Radar,
  LayoutDashboard,
  Zap,
  Sparkles,
  Users,
  BarChart3,
} from "lucide-react";

const modules = [
  {
    icon: Radar,
    name: "Sentinel Engine",
    metric: "14 days early",
    metricLabel: "churn detection",
    description:
      "ML risk scoring with SHAP-explainable signals across 47 behavioral inputs — attendance, assessments, login depth, payment friction.",
  },
  {
    icon: LayoutDashboard,
    name: "Coach Console",
    metric: "60% less time",
    metricLabel: "on mentor review",
    description:
      "Daily ranked at-risk queue with the Whisper Layer — exact reasons each student is slipping, exact playbook to intervene.",
  },
  {
    icon: Zap,
    name: "Pulse Interventions",
    metric: "55% success rate",
    metricLabel: "intervention to save",
    description:
      "A/B-tested WhatsApp and SMS nudges, auto-routed mentor escalations, outcome tracking. Stop guessing what works.",
  },
  {
    icon: Sparkles,
    name: "Tara AI Tutor",
    metric: "3 modes",
    metricLabel: "Saathi · Strategist · Guru",
    description:
      "White-label NCERT-grounded tutor with Indian-context analogies. Catches doubts before they become disengagement.",
  },
  {
    icon: Users,
    name: "Parent Visibility",
    metric: "Encourage-first",
    metricLabel: "stakeholder loop",
    description:
      "Parent-facing dashboards that build trust without triggering panic. Parents who feel informed stop pulling their kids out.",
  },
  {
    icon: BarChart3,
    name: "Command Center",
    metric: "Real-time",
    metricLabel: "cohort + revenue health",
    description:
      "Institute leadership view — cohort retention curves, churn-reason breakdowns, payment health, revenue forecasting.",
  },
];

export default function Features() {
  return (
    <section className="bg-white">
      <div className="mx-auto max-w-7xl px-6 py-20 md:py-28">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600">
            The platform
          </p>
          <h2 className="mt-3 font-display text-3xl md:text-4xl font-bold tracking-tight text-slate-900">
            Six modules. One retention loop.
          </h2>
          <p className="mt-4 text-lg text-slate-600 leading-relaxed">
            JEET sits between your institute's data and your mentors' daily
            workflow — predicting churn, surfacing reasons, and routing the
            right intervention at the right time.
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((m) => {
            const Icon = m.icon;
            return (
              <div
                key={m.name}
                className="group rounded-xl border border-slate-200 bg-white p-6 hover:border-indigo-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="rounded-lg bg-indigo-50 p-2.5">
                    <Icon className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-slate-900">
                      {m.metric}
                    </div>
                    <div className="text-xs text-slate-500">{m.metricLabel}</div>
                  </div>
                </div>

                <h3 className="mt-5 text-lg font-semibold text-slate-900">
                  {m.name}
                </h3>
                <p className="mt-2 text-sm text-slate-600 leading-relaxed">
                  {m.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
