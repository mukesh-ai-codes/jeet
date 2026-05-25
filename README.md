# JEET — AI-Driven Retention Platform for JEE/NEET Aspirants

> Predictive intelligence that prevents student churn before it happens.

JEET is an AI-first EdTech platform built for India's competitive exam ecosystem. Where traditional platforms detect dropouts after they occur, JEET predicts churn 14–30 days in advance and triggers personalized interventions that lift retention by an estimated 35–50%.

## The Problem

Indian EdTech operates on broken unit economics:
- **CAC:** ₹8,000–₹15,000 per enrolled student
- **Early dropout:** 55–65% of students disengage within the first 90 days
- **Detection:** Most platforms catch churn only after missed payments — too late

JEET treats retention as a **prediction problem**, not a remediation one.

## What Makes JEET Different

| Feature | What It Does |
|---------|--------------|
| **Sentinel Engine** | XGBoost + SHAP model predicting 90-day churn probability with per-student explainability |
| **Time-to-Churn Forecasting** | Survival analysis (Cox model) predicting *when* a student will drop — not just *if* |
| **Counterfactual Interventions** | "What-if" engine showing which actions reduce risk most |
| **Drishti AI Tutor** | RAG chatbot grounded in real NCERT + PYQ content with clickable citations |
| **Pulse Intervention System** | Tiered automated workflow: in-app nudges → parent WhatsApp → mentor escalation |
| **A/B Testing Framework** | Measures which interventions actually move retention |
| **Coach Console** | Mentor dashboard with AI-prepared talking points before every call |
| **Command Center** | Admin analytics: cohort retention curves, intervention ROI, model drift monitoring |

## Tech Stack

**Frontend:** Next.js 15 · TypeScript · Tailwind CSS · shadcn/ui · Recharts
**Backend:** FastAPI · SQLAlchemy · Alembic · PostgreSQL · Redis
**ML/AI:** XGBoost · SHAP · lifelines · DiCE · ChromaDB · Groq (Llama 3.3 70B)
**Infra:** Vercel · Railway · Supabase · GitHub Actions · MLflow · PostHog

## Architecture

See [`docs/architecture/`](docs/architecture/) for system diagrams and design rationale.

## Status

🚧 **Active Development** — Day 1 of 14-day execution sprint.

## Author

**Mukesh J** — IIM Ahmedabad EPAIB · Built as a portfolio-grade demonstration of production AI systems for EdTech retention.

## License

MIT — see [LICENSE](LICENSE).