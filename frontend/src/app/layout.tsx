import type { Metadata } from "next";
import { Inter, Lora, Hind } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const lora = Lora({
  subsets: ["latin"],
  variable: "--font-lora",
  display: "swap",
});

const hind = Hind({
  subsets: ["devanagari", "latin"],
  weight: ["400", "500", "600"],
  variable: "--font-hind",
  display: "swap",
});

export const metadata: Metadata = {
  title: "JEET — Retention OS for Coaching Institutes",
  description:
    "AI-powered churn prediction and intervention infrastructure for India's coaching industry. Catch dropouts 14 days early. Give your institute its LTV back.",
  keywords: [
    "EdTech",
    "retention",
    "coaching",
    "JEE",
    "NEET",
    "churn prediction",
    "India",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body
        className={`${inter.variable} ${lora.variable} ${hind.variable} antialiased min-h-screen bg-background text-foreground`}
      >
        {children}
      </body>
    </html>
  );
}