import Link from "next/link";
import { Button } from "@/components/ui/button";
import Logo from "@/components/shared/Logo";

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-white/70 border-b border-zinc-200">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/">
          <Logo size="md" />
        </Link>
        <div className="flex items-center gap-2">
          <Link
            href="#features"
            className="hidden sm:inline-flex px-3 py-2 text-sm text-zinc-700 hover:text-zinc-900"
          >
            Product
          </Link>
          <Link
            href="#plans"
            className="hidden sm:inline-flex px-3 py-2 text-sm text-zinc-700 hover:text-zinc-900"
          >
            Pricing
          </Link>
          <Link href="/login">
            <Button variant="ghost" size="sm">
              Sign in
            </Button>
          </Link>
          <Link href="#plans">
            <Button size="sm">Book a demo</Button>
          </Link>
        </div>
      </div>
    </nav>
  );
}