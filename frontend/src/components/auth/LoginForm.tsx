"use client";

/**
 * LoginForm — email/password form for /login.
 *
 * Responsibilities:
 *   1. Validate email/password with zod (instant client-side feedback)
 *   2. Submit to /api/auth/login via useAuth().login()
 *   3. Show clear error messages on failure
 *   4. Redirect to role-appropriate landing page on success
 *
 * Owned by: Phase 4, Day 12.
 */

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, AlertCircle, Eye, EyeOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useAuth } from "@/hooks/useAuth";
import { getErrorMessage } from "@/lib/api";
import { landingPathFor } from "@/lib/routes";

// Validation schema — runs in the browser before any network call.
const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

// Demo credentials displayed in the dev-only hint box. Remove on Day 26.
const DEMO_ACCOUNTS = [
  { role: "Admin",   email: "admin1@jeet.com" },
  { role: "Mentor",  email: "arjun5581@gmail.com" },
  { role: "Student", email: "aakash931@gmail.com" },
];

export default function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  const [submitError, setSubmitError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: LoginFormValues) {
    setSubmitError(null);
    try {
      const user = await login(values);

      const requestedNext = searchParams.get("next");
      const destination = requestedNext || landingPathFor(user);

      router.replace(destination);
    } catch (err) {
      setSubmitError(getErrorMessage(err));
    }
  }

  // One-click demo login during dev — clicks a chip to prefill the form
  function fillDemo(email: string) {
    setValue("email", email, { shouldValidate: true });
    setValue("password", "demo123!", { shouldValidate: true });
    setSubmitError(null);
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
      {/* Email */}
      <div className="space-y-2">
        <Label htmlFor="email" className="text-sm font-medium text-slate-900">
          Work email
        </Label>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          placeholder="you@institute.com"
          aria-invalid={!!errors.email}
          {...register("email")}
          className="h-11"
        />
        {errors.email && (
          <p className="text-xs text-red-600">{errors.email.message}</p>
        )}
      </div>

      {/* Password */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="password" className="text-sm font-medium text-slate-900">
            Password
          </Label>
          <button
            type="button"
            tabIndex={-1}
            onClick={() => setShowPassword((s) => !s)}
            className="text-xs text-slate-500 hover:text-slate-700 inline-flex items-center gap-1"
          >
            {showPassword ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>
        <Input
          id="password"
          type={showPassword ? "text" : "password"}
          autoComplete="current-password"
          aria-invalid={!!errors.password}
          {...register("password")}
          className="h-11"
        />
        {errors.password && (
          <p className="text-xs text-red-600">{errors.password.message}</p>
        )}
      </div>

      {submitError && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
          <span>{submitError}</span>
        </div>
      )}

      <Button
        type="submit"
        disabled={isSubmitting}
        className="w-full h-11 bg-indigo-600 hover:bg-indigo-700"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Signing in…
          </>
        ) : (
          "Sign in"
        )}
      </Button>

      {/* Demo credentials hint — remove this on Day 26 when going live */}
      <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-3 text-xs">
        <div className="flex items-center justify-between mb-2">
          <p className="font-semibold text-slate-700">Try the demo</p>
          <span className="text-slate-400">
            Password: <span className="font-mono text-slate-600">demo123!</span>
          </span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {DEMO_ACCOUNTS.map((acc) => (
            <button
              key={acc.email}
              type="button"
              onClick={() => fillDemo(acc.email)}
              className="rounded-full border border-slate-300 bg-white px-2.5 py-1 text-slate-700 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700 transition"
            >
              {acc.role}
            </button>
          ))}
        </div>
        <p className="mt-2 text-slate-500">
          Click a role to prefill credentials.
        </p>
      </div>
    </form>
  );
}
