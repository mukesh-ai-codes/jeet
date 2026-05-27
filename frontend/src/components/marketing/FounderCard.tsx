import Image from "next/image";

export default function FounderCard() {
  return (
    <section className="py-24 sm:py-28 bg-white">
      <div className="max-w-4xl mx-auto px-6">
        <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-8 sm:p-12">
          <div className="flex flex-col sm:flex-row gap-8 items-start">
            <div className="shrink-0">
              <div className="relative w-24 h-24 sm:w-28 sm:h-28 rounded-full overflow-hidden ring-4 ring-white shadow-md">
                <Image
                  src="/founder.jpg"
                  alt="Mukesh Jain, founder of JEET"
                  fill
                  className="object-cover"
                  sizes="(max-width: 640px) 96px, 112px"
                  priority
                />
              </div>
            </div>

            <div className="flex-1">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-wider">
                Founder note
              </p>
              <h2 className="mt-2 font-display text-2xl sm:text-3xl text-zinc-900 tracking-tight">
                Why I&apos;m building JEET
              </h2>
              <p className="mt-4 text-zinc-700 leading-relaxed">
                Mukesh Jain spent years inside Indian EdTech as VP and Product
                Head — watching institutes hemorrhage student LTV to silent
                dropouts. He&apos;s building JEET to fix it.
              </p>
              <div className="mt-5 flex flex-wrap gap-x-5 gap-y-1 text-sm text-zinc-500">
                <span>IIM Ahmedabad</span>
                <span className="text-zinc-300">·</span>
                <span>NIT Jaipur</span>
                <span className="text-zinc-300">·</span>
                <span>Ex-VP & Product Head, EdTech</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}