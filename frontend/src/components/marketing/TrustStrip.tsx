import { Shield, Server, Lock, FileCheck } from "lucide-react";

const trust = [
  {
    icon: Shield,
    title: "DPDP Act compliant",
    description: "Aligned with India's Digital Personal Data Protection Act.",
  },
  {
    icon: Server,
    title: "Data hosted in India",
    description: "AWS Mumbai region. Your students' data never leaves India.",
  },
  {
    icon: Lock,
    title: "Role-based access",
    description:
      "Mentors see their cohort. Admins see their institute. Zero data leakage.",
  },
  {
    icon: FileCheck,
    title: "Audit-ready logs",
    description: "Every prediction, every intervention, every access — logged.",
  },
];

export default function TrustStrip() {
  return (
    <section className="bg-slate-900 text-white">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="text-center max-w-2xl mx-auto">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-300">
            Trust & security
          </p>
          <h2 className="mt-3 font-display text-2xl md:text-3xl font-bold">
            Built for institutes that take student data seriously.
          </h2>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {trust.map((t) => {
            const Icon = t.icon;
            return (
              <div key={t.title} className="rounded-xl bg-slate-800/50 p-5 border border-slate-700">
                <Icon className="h-5 w-5 text-indigo-300" />
                <h3 className="mt-4 text-sm font-semibold text-white">
                  {t.title}
                </h3>
                <p className="mt-1 text-xs text-slate-400 leading-relaxed">
                  {t.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
