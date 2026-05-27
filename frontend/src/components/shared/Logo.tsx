import { cn } from "@/lib/utils";

type LogoVariant = "default" | "white";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  showWordmark?: boolean;
  variant?: LogoVariant;
  className?: string;
}

/**
 * Signal Waves logo — orange center dot + 3 concentric indigo arcs.
 *
 * Variants:
 *   "default" — indigo arcs + zinc wordmark, for light backgrounds
 *   "white"   — white arcs + white wordmark, for dark/indigo backgrounds
 *
 * The orange center dot stays consistent across variants — it's the
 * brand's anchor color and remains visible on both light and dark.
 */
export default function Logo({
  size = "md",
  showWordmark = true,
  variant = "default",
  className,
}: LogoProps) {
  const dimensions = {
    sm: { mark: 20, text: "text-lg" },
    md: { mark: 28, text: "text-2xl" },
    lg: { mark: 40, text: "text-4xl" },
  };

  const { mark, text } = dimensions[size];

  // Color theming
  const arcColor = variant === "white" ? "#FFFFFF" : "#4F46E5";
  const wordmarkClass = variant === "white" ? "text-white" : "text-zinc-900";

  return (
    <div className={cn("inline-flex items-center gap-2.5", className)}>
      <svg
        width={mark}
        height={mark}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-label="JEET logo"
      >
        <circle cx="20" cy="20" r="6" fill="#F97316" />
        <path
          d="M 9 20 A 11 11 0 0 1 31 20"
          fill="none"
          stroke={arcColor}
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <path
          d="M 4 20 A 16 16 0 0 1 36 20"
          fill="none"
          stroke={arcColor}
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.55"
        />
        <path
          d="M 0 20 A 20 20 0 0 1 40 20"
          fill="none"
          stroke={arcColor}
          strokeWidth="1.5"
          strokeLinecap="round"
          opacity="0.3"
        />
      </svg>
      {showWordmark && (
        <span className={cn("font-bold tracking-tight", text, wordmarkClass)}>
          JEET
        </span>
      )}
    </div>
  );
}
