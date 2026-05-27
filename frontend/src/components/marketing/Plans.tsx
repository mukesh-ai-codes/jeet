"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";

interface Plan {
  slug: string;
  name: string;
  tagline: string;
  price: string;
  priceCaption: string;
  features: string[];
  cta: string;
  highlight?: boolean;
}

const PLANS: Plan[] = [
  {
    slug: "trial",
    name: "Trial",
    tagline: "Test JEET on your cohort",
    price: "Free",
    priceCaption: "30-day pilot",
    features: [
      "Up to 50 students",
      "Sentinel Engine (read-only)",
      "Basic Coach Console",
      "Standard retention dashboards",
      "Email support",
    ],
    cta: "Start pilot",
  },
  {
    slug: "professional",
    name: "Professional",
    tagline: "For mid-sized coaching chains",
    price: "₹12,000",
    priceCaption: "per cohort / month",
    features: [
      "Unlimited cohorts",
      "Full Sentinel Engine + intervention APIs",
      "Coach Console + Whisper Layer",
      "Pulse Interventions (WhatsApp + SMS)",
      "Tara AI Tutor (white-label)",
      "Parent Dashboard",
      "Priority support · Slack channel",
    ],
    cta: "Book a demo",
    highlight: true,
  },
  {
    slug: "enterprise",
    name: "Enterprise",
    tagline: "For institute groups at scale",
    price: "Custom",
    priceCaption: "50+ cohorts",
    features: [
      "Everything in Professional, plus:",
      "Custom integrations (LMS, CRM, SIS)",
      "Dedicated Customer Success Manager",
      "On-premise / VPC deployment option",
      "Custom ML model training",
      "SLA + 24×7 escalation",
      "Quarterly retention strategy reviews",
    ],
    cta: "Talk to sales",
  },
];

export default function Plans() {
  return (
    <section id="plans" className="py-24 sm:py-32 bg-zinc-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-2xl mx-auto">
          <p className="text-sm font-semibold text-indigo-600 uppercase tracking-wide">
            Pricing
          </p>
          <h2 className="mt-3 font-display text-4xl sm:text-5xl tracking-tight text-zinc-900">
            Priced for the institute you run.
          </h2>
          <p className="mt-4 text-lg text-zinc-600">
            Start with a free 30-day pilot on one cohort. Scale to your full
            operation when the retention numbers speak for themselves.
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.slug}
              className={`relative p-8 rounded-2xl bg-white transition-all ${
                plan.highlight
                  ? "border-2 border-indigo-600 shadow-xl md:scale-105"
                  : "border border-zinc-200 shadow-sm"
              }`}
            >
              {plan.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-indigo-600 text-white text-xs font-semibold rounded-full">
                  Most institutes start here
                </div>
              )}
              <h3 className="text-2xl font-bold text-zinc-900">{plan.name}</h3>
              <p className="mt-1 text-sm text-zinc-500">{plan.tagline}</p>
              <div className="mt-6 flex items-baseline gap-2">
                <span className="text-4xl font-bold text-zinc-900">
                  {plan.price}
                </span>
                <span className="text-zinc-500 text-sm">{plan.priceCaption}</span>
              </div>
              <ul className="mt-8 space-y-3">
                {plan.features.map((feat) => (
                  <li key={feat} className="flex items-start gap-2 text-sm text-zinc-700">
                    <Check className="w-4 h-4 mt-0.5 text-emerald-600 shrink-0" />
                    <span>{feat}</span>
                  </li>
                ))}
              </ul>
              <Link href="/login" className="mt-8 block">
                <Button
                  className="w-full"
                  variant={plan.highlight ? "default" : "outline"}
                  size="lg"
                >
                  {plan.cta}
                </Button>
              </Link>
            </div>
          ))}
        </div>

        <p className="mt-12 text-center text-sm text-zinc-500">
          Looking for the student experience?{" "}
          <Link href="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">
            Try our student demo →
          </Link>
        </p>
      </div>
    </section>
  );
}