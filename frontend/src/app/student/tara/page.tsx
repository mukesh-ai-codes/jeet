"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, ArrowLeft } from "lucide-react";
import Link from "next/link";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import { taraApi } from "@/lib/api";

type Turn = { role: "student" | "tara"; text: string; sources?: string[] };

const MODES = [
  { id: "saathi", label: "Saathi", hint: "Warm & motivating" },
  { id: "strategist", label: "Strategist", hint: "Exam-focused" },
  { id: "guru", label: "Guru", hint: "Deep concepts" },
] as const;

export default function TaraPage() {
  const [turns, setTurns] = useState<Turn[]>([
    { role: "tara", text: "Hey! I'm Tara, your study companion. Ask me anything — a concept, a doubt, or just tell me how prep is going." },
  ]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<string>("saathi");
  const [sending, setSending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [turns, sending]);

  async function send() {
    const msg = input.trim();
    if (!msg || sending) return;
    setInput("");
    setTurns((t) => [...t, { role: "student", text: msg }]);
    setSending(true);
    try {
      const memory = turns.slice(-6).map((t) => ({ role: t.role === "tara" ? "tara" : "student", text: t.text }));
      const res = await taraApi.chat({ message: msg, mode, memory });
      setTurns((t) => [...t, { role: "tara", text: res.reply, sources: (res.sources || []).filter(Boolean) as string[] }]);
    } catch {
      setTurns((t) => [...t, { role: "tara", text: "I had trouble responding just now — mind trying again?" }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <ProtectedRoute allowedRoles={["student"]}>
      <AppShell>
        <div className="mx-auto flex h-[calc(100vh-9rem)] max-w-3xl flex-col">
          <div className="mb-4">
            <Link href="/student" className="mb-2 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
              <ArrowLeft className="h-4 w-4" /> Back to dashboard
            </Link>
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <h1 className="font-display text-xl font-bold text-slate-900">Tara</h1>
                <p className="text-xs text-slate-500">RAG-grounded · NCERT-aware</p>
              </div>
            </div>
          </div>

          <div className="mb-3 flex flex-wrap gap-2">
            {MODES.map((m) => (
              <button key={m.id} onClick={() => setMode(m.id)}
                className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${
                  mode === m.id ? "border-indigo-600 bg-indigo-50 text-indigo-700"
                  : "border-slate-200 text-slate-600 hover:border-slate-300"}`}>
                {m.label} <span className="text-slate-400">· {m.hint}</span>
              </button>
            ))}
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-4">
            {turns.map((t, i) => (
              <div key={i} className={`flex ${t.role === "student" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  t.role === "student" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-800"}`}>
                  <div className="whitespace-pre-wrap">{t.text}</div>
                  {t.sources && t.sources.length > 0 && (
                    <div className="mt-2 text-xs text-slate-500">Grounded in: {t.sources.join(", ")}</div>
                  )}
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-slate-400">Tara is thinking…</div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          <div className="mt-3 flex gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
              placeholder="Ask Tara anything…"
              className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm focus:border-indigo-400 focus:outline-none"
              disabled={sending} />
            <button onClick={send} disabled={sending || !input.trim()}
              className="flex items-center justify-center rounded-xl bg-indigo-600 px-4 text-white disabled:opacity-40">
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </AppShell>
    </ProtectedRoute>
  );
}
