import Logo from "@/components/shared/Logo";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-16">
        {/* Bilingual chorus — the emotional anchor */}
        <div className="mb-12 text-center">
          <p
            className="text-xl md:text-2xl text-slate-900"
            style={{
              fontFamily:
                'var(--font-hind), "Noto Sans Devanagari", system-ui, sans-serif',
              fontWeight: 500,
              lineHeight: 1.6,
            }}
          >
            हर स्टूडेंट टिकता है। हर इंस्टीट्यूट जीतता है।
          </p>
          <p className="mt-3 text-sm text-slate-500">
            Every student stays. Every institute wins.
          </p>
        </div>

        {/* 3-column footer */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pt-8 border-t border-slate-100">
          <div className="md:col-span-1">
            <Logo size="md" />
            <p className="mt-4 text-sm text-slate-600 max-w-xs">
              Retention OS for India's coaching industry. Catch dropouts before
              they happen.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Product</h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>Sentinel Engine</li>
              <li>Coach Console</li>
              <li>Pulse Interventions</li>
              <li>Tara AI Tutor</li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Company</h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>About</li>
              <li>Pricing</li>
              <li>Book a demo</li>
              <li>Contact</li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Trust</h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>DPDP Act compliant</li>
              <li>Data hosted in India</li>
              <li>Role-based access</li>
              <li>Privacy policy</li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-6 border-t border-slate-100 text-xs text-slate-500 text-center">
          © 2026 JEET. Stop dropouts before they start.
        </div>
      </div>
    </footer>
  );
}
