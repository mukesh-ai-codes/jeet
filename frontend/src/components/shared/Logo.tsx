import { cn } from "@/lib/utils";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  showWordmark?: boolean;
  className?: string;
}

export default function Logo({ size = "md", showWordmark = true, className }: LogoProps) {
  const dimensions = {
    sm: { mark: 20, text: "text-lg" },
    md: { mark: 28, text: "text-2xl" },
    lg: { mark: 40, text: "text-4xl" },
  };

  const { mark, text } = dimensions[size];

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
          stroke="#4F46E5"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <path
          d="M 4 20 A 16 16 0 0 1 36 20"
          fill="none"
          stroke="#4F46E5"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.55"
        />
        <path
          d="M 0 20 A 20 20 0 0 1 40 20"
          fill="none"
          stroke="#4F46E5"
          strokeWidth="1.5"
          strokeLinecap="round"
          opacity="0.3"
        />
      </svg>
      {showWordmark && (
        <span className={cn("font-bold tracking-tight text-zinc-900", text)}>
          JEET
        </span>
      )}
    </div>
  );
}
