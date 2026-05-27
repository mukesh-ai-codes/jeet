import { Building2 } from "lucide-react";

export default function LogoStrip() {
  return (
    <section className="bg-white">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-slate-500">
          Built for coaching institutes like yours
        </p>

        <div className="mt-8 grid grid-cols-3 md:grid-cols-6 gap-6 items-center">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center justify-center h-12 rounded-md border border-dashed border-slate-200 bg-slate-50/50"
            >
              <Building2 className="h-5 w-5 text-slate-300" />
              <span className="ml-2 text-xs text-slate-400">Institute</span>
            </div>
          ))}
        </div>

        <p className="mt-8 text-center text-sm text-slate-600">
          <span className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-4 py-1.5 text-indigo-700 font-medium">
            <span className="h-1.5 w-1.5 rounded-full bg-indigo-600 animate-pulse" />
            Early access cohort opening for 10 institutes
          </span>
        </p>
      </div>
    </section>
  );
}
