const stats = [
  {
    value: "60–70%",
    label: "of coaching students drop out before exam day",
    tone: "alarm",
  },
  {
    value: "14 days",
    label: "early warning, before silent disengagement turns into churn",
    tone: "signal",
  },
  {
    value: "₹10L–₹50L",
    label: "in LTV recovered per 5% retention lift, per institute",
    tone: "outcome",
  },
];

export default function StatRow() {
  return (
    <section className="border-y border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {stats.map((s, i) => (
            <div
              key={i}
              className="text-center md:text-left md:border-l md:first:border-l-0 md:pl-8 md:first:pl-0"
            >
              <div
                className={`text-3xl md:text-4xl font-bold ${
                  s.tone === "alarm"
                    ? "text-orange-600"
                    : s.tone === "signal"
                    ? "text-indigo-600"
                    : "text-emerald-600"
                }`}
              >
                {s.value}
              </div>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed">
                {s.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
