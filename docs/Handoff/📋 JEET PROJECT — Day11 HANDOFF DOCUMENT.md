📋 JEET PROJECT — COMPLETE HANDOFF DOCUMENT  
Date of handoff: May 27, 2026  
Active session day: Day 11 of 28  
Prepared by: Claude (this conversation)  
For: Continuation in a new chat session

1\. PROJECT OVERVIEW  
Project Name  
JEET — Retention OS for India's Coaching Industry  
Core Objective  
Build a B2B SaaS platform that uses AI to predict and prevent student dropouts in Indian JEE/NEET coaching institutes. The platform catches at-risk students 14 days before disengagement, surfaces why they're at risk, and gives mentors a playbook to intervene before churn happens.  
Target Users (B2B)

Primary buyer: Coaching institutes (Allen/Aakash-scale chains down to mid-tier 5–50 cohort operations) — they pay for the platform  
Platform users inside an institute:

Institute admins/founders — see Command Center analytics, cohort retention, revenue health  
Mentors/coaches — use Coach Console with daily at-risk student queue  
Students — use student dashboard, lessons, AI tutor (Tara)  
Parents — use parent dashboard with encouragement-first messaging

Main Problem Being Solved

Indian coaching institutes lose 60–70% of students before exam day  
Churn is silent and predictable but invisible without behavioral analytics  
A 5% retention lift \= ₹10L–₹50L in saved LTV per institute  
No existing Indian B2B SaaS owns this category (Civitas/Othot/Mainstay exist globally but not in India)

Business Model  
B2B SaaS — per-cohort/per-month pricing:  
TierPriceAudienceTrialFree 30 daysUp to 50 students, pilotProfessional₹12,000/cohort/monthMid-sized chains (5–50 cohorts)EnterpriseCustom50+ cohorts, custom integrations, dedicated CSM  
Key Features (6 Modules)

Sentinel Engine — ML churn prediction with SHAP-explainable risk scores  
Coach Console — Mentor dashboard with daily ranked at-risk queue \+ Whisper Layer insights  
Pulse Interventions — Automated WhatsApp/SMS nudges \+ mentor-routed escalations, A/B tested  
Tara AI Tutor — White-label NCERT-grounded tutor with Indian-context analogies (3 modes: Saathi/Strategist/Guru)  
Parent Visibility — Encouragement-first stakeholder messaging  
Command Center — Real-time institute leadership analytics (cohort curves, churn breakdowns, revenue forecasting)

2\. CURRENT PROJECT STATUS  
✅ COMPLETED (Days 1–11)  
DayPhaseDeliverable1–2FoundationmacOS env setup, GitHub repo, 14-table PostgreSQL schema3Data simulator5,622 users (3,000 students with 8 archetypes, 2,567 parents, 50 mentors, 5 admins)4Catalog \+ commerce60 cohorts, 507 NCERT lessons, 3,000 enrollments, 3,541 payments \= ₹6.81 Cr captured revenue5Behavior simulation1,470,075 events, 70,891 attendance, 33,498 assessments across 120 days6ML feature store4 SQL feature views7FastAPI backend foundationJWT auth with bcrypt, role-based access8Dashboard APIsStudent/mentor dashboards \+ Whisper Layer rules engine9Course discovery APIsLesson recommendations, parent dashboard, event tracking10Analytics \+ interventions25 production endpoints total, \~3,200 lines Python, 200 historical interventions seeded11Frontend bootstrap \+ B2B rebrandNext.js 16.2.6 landing page live at localhost:3000  
🔄 PARTIALLY COMPLETED (Active Day 11\)

Landing page is live and working with B2B positioning  
Logo (Signal Waves design) implemented as reusable React component  
Hero illustration (Coaching A → student → JEET layer → Coaching B with 3 risk-signal pills) shipped  
6 module cards live (Sentinel Engine, Coach Console, Pulse Interventions, Tara AI Tutor, Parent Visibility, Command Center)  
B2B pricing tiers live (Trial/Professional/Enterprise)  
Bilingual chorus in Devanagari script: "हर स्टूडेंट टिकता है। हर इंस्टीट्यूट जीतता है।"  
Founder card added with Mukesh Jain's photo \+ polished bio  
Final pending action before Day 12: User needs to confirm Devanagari \+ founder card render correctly, then commit Day 11

⏭️ NOT STARTED (Days 12–28)  
DayPhaseDeliverable12Auth flowLogin page, JWT storage, route protection, 8-question onboarding wizard13Student dashboardCourse viewer, weak chapters, recommendations14Parent dashboardChild detail view, encouragement messaging15Coach Console \+ Command CenterMentor \+ admin dashboards16PolishMobile responsive, dark mode, animations17–19ML PipelineXGBoost churn classifier \+ SHAP \+ lifelines survival analysis \+ DiCE counterfactuals20–23Tara AI TutorRAG (ChromaDB \+ NCERT) \+ Analogy Engine \+ 3 modes \+ memory \+ frustration detection24–25Pulse InterventionsA/B testing framework26–28LaunchDeployment (Vercel \+ Railway \+ Supabase), README, demo video, LinkedIn launch post  
Current Blockers / Issues  
None active. Last bug fixed: empty Logo.tsx file caused "Element type is invalid" runtime error — resolved by creating file with cat \> ... EOF heredoc approach.  
Current Working State

Backend: Running on http://localhost:8000 (uvicorn with \--reload). All 25 endpoints functional. Auth verified working. Cohort deep-dive returning real data (NEET-2028 Delhi Alpha cohort: 31 students, ₹15.24L revenue, 90.32% week-12 retention).  
Frontend: Running on http://localhost:3000 (Next.js Turbopack). Landing page renders fully with all 6 components.  
Database: PostgreSQL on localhost:5432/jeet\_dev. All seed data intact.

3\. TECH STACK  
Backend  
LayerTechnologyLanguagePython 3.12FrameworkFastAPIASGI serverUvicornORM/DB driverSQLAlchemy \+ psycopg2AuthJWT (PyJWT) \+ bcrypt password hashingValidationPydantic v2Data simulationFaker (Indian locale where applicable)Package managerpipVirtual environmentvenv (/Users/mj/Projects/jeet/.venv)  
Database  
LayerTechnologyRDBMSPostgreSQL 16 (local install)Database namejeet\_devUsermjExtensionsuuid-ossp, pgcryptoGUI toolTablePlus (used for inspection)  
Frontend  
LayerTechnologyFrameworkNext.js 16.2.6 (App Router)LanguageTypeScriptBuild toolTurbopack (dev)StylingTailwind CSS v4Component libraryshadcn/ui (Radix primitives, "New York" / Nova preset)Iconslucide-reactHTTP clientaxiosFormsreact-hook-form \+ zodDatesdate-fnsChartsrechartsAnimationframer-motionUtilitiesclsx \+ tailwind-mergeNode versionv20.20.2npm version10.8.2  
Fonts (Google Fonts)

Inter — UI body (--font-inter)  
Lora — Display/serif headlines (--font-lora)  
Hind — Devanagari \+ Latin bilingual (--font-hind)

Planned (Days 17+)

ML: XGBoost, SHAP, lifelines, DiCE  
AI Tutor: ChromaDB (vector DB), OpenAI/Anthropic API for LLM  
Deployment (Day 26+): Vercel (frontend), Railway (backend), Supabase (production DB)

4\. DEVELOPMENT ENVIRONMENT  
OS & Hardware

Machine: MacBook Air M3 (2024)  
OS: macOS 26.3  
Shell: zsh (default)  
User home: /Users/mj

IDE

VS Code (opened with code . from project root)

Ports  
PortService5432PostgreSQL8000FastAPI backend (uvicorn)3000Next.js frontend dev server  
Required Concurrent Terminals  
Two terminals must be running simultaneously:

Terminal 1: Backend (uvicorn) — must stay alive while developing  
Terminal 2: Frontend (npm run dev) — auto-reloads on file save

Setup Commands  
Start backend:  
bashcd \~/Projects/jeet  
source .venv/bin/activate  
cd backend  
uvicorn app.main:app \--reload \--port 8000  
Start frontend:  
bashcd \~/Projects/jeet/frontend  
npm run dev  
Database access:  
bashpsql \-U mj \-d jeet\_dev  
Environment Variables  
Backend .env (at /Users/mj/Projects/jeet/.env):  
DATABASE\_URL=postgresql://mj@localhost:5432/jeet\_dev  
NUM\_STUDENTS=3000  
NUM\_DAYS=120  
RANDOM\_SEED=42  
JWT\_SECRET\_KEY=\<long-random-string\>  
JWT\_ALGORITHM=HS256  
JWT\_EXPIRE\_HOURS=24  
BACKEND\_CORS\_ORIGINS=\["http://localhost:3000","http://localhost:5173"\]  
Frontend .env.local (at /Users/mj/Projects/jeet/frontend/.env.local):  
NEXT\_PUBLIC\_API\_URL=http://localhost:8000  
Test Credentials (Synthetic Users)

Demo password (all users): demo123\!  
Sample admin email: admin1@jeet.com  
Pattern: student1@jeet.com, parent1@jeet.com, mentor1@jeet.com

5\. COMPLETE FOLDER STRUCTURE  
\~/Projects/jeet/  
├── .env                          \# Backend environment variables  
├── .venv/                        \# Python virtual environment (gitignored)  
├── .gitignore  
├── README.md                     \# (basic — needs Day 26 expansion)  
├── docs/  
│   └── product/  
│       └── ai-tutor-vision-roadmap.md  \# Future Tara features (deferred to docs)  
│  
├── data/  
│   ├── schema/                   \# SQL schema files run in order  
│   │   ├── 01\_extensions.sql  
│   │   ├── 02\_enums.sql  
│   │   ├── 03\_users.sql  
│   │   ├── 04\_catalog.sql  
│   │   ├── 05\_commerce.sql  
│   │   ├── 06\_behavior.sql  
│   │   ├── 07\_assessments.sql  
│   │   ├── 08\_interventions.sql  
│   │   ├── 09\_feature\_views.sql  
│   │   └── run\_all.sh  
│   └── scripts/                  \# Python data simulation  
│       ├── config.py  
│       ├── db.py  
│       ├── 01\_seed\_users.py  
│       ├── 02\_seed\_catalog\_and\_commerce.py  
│       ├── 03\_seed\_behavior.py  
│       └── simulator/  
│           ├── indian\_identity.py  
│           ├── archetypes.py  
│           ├── generators.py  
│           ├── curriculum.py  
│           ├── calendar\_effects.py  
│           ├── student\_state.py  
│           ├── behavior\_engine.py  
│           ├── event\_factory.py  
│           └── loader.py  
│  
├── backend/  
│   ├── requirements.txt  
│   └── app/  
│       ├── main.py               \# FastAPI app entry with CORS, lifespan, router includes  
│       ├── core/  
│       │   ├── config.py         \# Settings via Pydantic BaseSettings  
│       │   ├── database.py       \# SQLAlchemy engine \+ get\_db dependency  
│       │   ├── security.py       \# JWT create/verify \+ bcrypt helpers  
│       │   └── deps.py           \# require\_role, get\_current\_user dependencies  
│       ├── schemas/              \# Pydantic response/request models  
│       │   ├── auth.py  
│       │   ├── student.py  
│       │   ├── parent.py  
│       │   ├── mentor.py  
│       │   ├── admin.py  
│       │   ├── course.py  
│       │   └── analytics.py  
│       └── api/                  \# Route modules  
│           ├── auth.py  
│           ├── health.py  
│           ├── students.py  
│           ├── parents.py  
│           ├── mentors.py  
│           ├── admin.py  
│           ├── courses.py  
│           ├── analytics.py  
│           └── interventions.py  
│  
└── frontend/                     \# Next.js 16.2.6 app  
    ├── .env.local  
    ├── .gitignore  
    ├── package.json  
    ├── tsconfig.json  
    ├── next.config.ts  
    ├── postcss.config.mjs  
    ├── eslint.config.mjs  
    ├── components.json           \# shadcn/ui config  
    ├── public/  
    │   ├── founder.jpg           \# Mukesh's headshot (just added)  
    │   ├── next.svg              \# default — can delete  
    │   └── vercel.svg            \# default — can delete  
    └── src/  
        ├── app/  
        │   ├── layout.tsx        \# Root with Inter \+ Lora \+ Hind fonts  
        │   ├── page.tsx          \# Home: Navbar \+ Hero \+ Features \+ FounderCard \+ Plans \+ Footer  
        │   ├── globals.css       \# Tailwind \+ JEET brand tokens  
        │   └── favicon.ico  
        ├── components/  
        │   ├── ui/               \# shadcn components (button, card, badge, etc — \~11 files)  
        │   ├── marketing/  
        │   │   ├── Navbar.tsx  
        │   │   ├── Hero.tsx      \# Contains HeroIllustration SVG inline  
        │   │   ├── Features.tsx  
        │   │   ├── FounderCard.tsx  
        │   │   ├── Plans.tsx     \# Hardcoded B2B tiers (NOT fetched from backend)  
        │   │   └── Footer.tsx  
        │   └── shared/  
        │       └── Logo.tsx      \# Signal Waves SVG \+ JEET wordmark  
        ├── lib/  
        │   ├── api.ts            \# Axios client with JWT interceptor  
        │   └── utils.ts          \# cn() helper (shadcn default)  
        ├── types/  
        │   └── index.ts          \# AuthUser, StudentDashboard, RiskTier, Program, etc.  
        └── hooks/                \# Empty placeholder for future hooks

6\. FRONTEND DETAILS  
Framework

Next.js 16.2.6 with App Router \+ TypeScript \+ Turbopack

Styling Approach

Tailwind CSS v4 (latest) with CSS variables via @theme inline block  
Custom JEET design tokens in globals.css:

\--jeet-indigo (\#4F46E5) — primary brand  
\--jeet-orange (\#F97316) — accent/interventions  
Midnight \#1e1b4b — text  
Bone \#FAFAF9 — backgrounds

Risk tier utility classes: .tier-urgent, .tier-critical, .tier-watch, .tier-stable  
Custom utilities: .font-display (Lora), .font-hindi (Hind), .gradient-indigo-soft, .animate-pulse-soft

Design Language

"Confident Calm" — Linear \+ Notion energy  
NOT cartoonish like BYJU'S, NOT corporate-sterile like Coursera  
Premium SaaS aesthetic — clean, intelligent, founder-friendly

Logo Design

Direction chosen: "Signal Waves" (option 06 from logo menu)  
Visual: Orange center dot \+ 3 concentric indigo arcs of decreasing opacity (1.0 → 0.55 → 0.3)  
Conveys: "We listen, we predict" — B2B infrastructure feel  
Reusable component at src/components/shared/Logo.tsx with sm/md/lg sizes

Components Built  
ComponentLocationPurposeLogoshared/Logo.tsxSignal Waves SVG \+ JEET wordmark, configurable sizeNavbarmarketing/Navbar.tsxSticky, blur-bg, JEET logo, Product/Pricing/Sign in/Book a demoHeromarketing/Hero.tsxTwo-column hero with inline HeroIllustration SVG componentFeaturesmarketing/Features.tsx6 module cards in 3×2 gridFounderCardmarketing/FounderCard.tsxPhoto \+ bio for Mukesh JainPlansmarketing/Plans.tsx3 B2B tiers (hardcoded, NOT API-fetched)Footermarketing/Footer.tsxLogo \+ chorus \+ 3-column links  
State Management

None yet. Will add Zustand or React Context on Day 12 for auth state.

Routing

App Router (file-based)  
Only / (home) implemented so far  
Day 12 adds: /login, /onboarding, /student, /parent, /mentor, /admin

UI/UX Decisions Made

App Router over Pages Router — modern Next.js, server components by default  
shadcn/ui over Material UI/Chakra — components copied into repo, no library lock-in, what Vercel/Linear/Cal.com use  
Hardcoded B2B pricing tiers — original API returned B2C student plans (₹8,999/₹24,999/₹49,999). For B2B rebrand, pricing is hardcoded in Plans.tsx. Backend /api/courses/programs endpoint still exists but is no longer called from landing page.  
Devanagari chorus — bilingual code-switch ("हर स्टूडेंट टिकता है। हर इंस्टीट्यूट जीतता है।") uses common spoken Hindi forms rather than purist Sanskrit (विद्यार्थी/संस्थान)  
Founder bio Variant A chosen — "Mukesh Jain spent years inside Indian EdTech as VP and Product Head — watching institutes hemorrhage student LTV to silent dropouts. He's building JEET to fix it. IIM Ahmedabad and NIT Jaipur alum."

Pending Frontend Tasks

Day 12: Login page \+ JWT flow \+ protected routes \+ onboarding wizard  
Day 13: Student dashboard \+ course viewer  
Day 14: Parent dashboard  
Day 15: Mentor Coach Console \+ Admin Command Center  
Day 16: Mobile responsiveness \+ dark mode \+ animations

7\. BACKEND DETAILS  
Framework

FastAPI with async support (though most routes are sync since SQLAlchemy is sync)  
Auto-generated Swagger docs at /docs

Authentication Flow

User POSTs to /api/auth/login (JSON) or /api/auth/token (OAuth2 form for Swagger)  
Backend verifies bcrypt password hash against DB  
Returns JWT signed with HS256, 24-hour expiry  
Frontend stores token in localStorage under key jeet\_access\_token  
Axios interceptor attaches Authorization: Bearer \<token\> to all requests  
Backend require\_role() dependency decodes JWT, checks role claim against allowed roles  
401 response triggers frontend interceptor to clear token and redirect to /login

Services / Business Logic Completed

Whisper Layer rules engine — translates 47 behavioral signals into mentor-readable intervention recommendations (rules-based, not LLM yet)  
Personalized lesson recommender — uses weak chapters from student feature view  
Risk scoring — 0-100 score with tier classification (stable/watch/critical/urgent/lost)  
Intervention effectiveness tracker — links interventions to subsequent retention outcomes  
Churn reason classifier — 5-bucket classification (academic/financial/engagement/peer/family)

Pending Backend Tasks

Day 17–19: Train actual XGBoost model, generate SHAP explanations, fit Cox survival model  
Day 20–23: ChromaDB ingestion of NCERT content, RAG retrieval endpoints, Tara conversation API  
Day 24–25: A/B test framework for intervention messages

8\. DATABASE DETAILS  
Database

PostgreSQL 16 (local install via Homebrew or Postgres.app)  
Database: jeet\_dev  
14 tables \+ 4 materialized feature views \+ interventions table \= 15 tables total

Core Tables  
TableKey ColumnsPurposeusersid (UUID), email, password\_hash, full\_name, role, phoneAll user types (student/parent/mentor/admin)user\_profilesuser\_id, grade, target\_exam, motivation\_score, weak\_subjectsStudent-specific profile datafamiliesid, primary\_parent\_user\_id, student\_user\_idParent-student linkageprogramsid, slug, name, price\_inr, duration\_monthsCourse programs (Starter/Pro/Mastermind in DB but UI uses B2B tiers)subjectsid, slug, name, program\_idPhysics/Chemistry/Bio/Mathchaptersid, subject\_id, name, ncert\_orderNCERT-aligned chapter listlessonsid, chapter\_id, title, type, duration\_min507 NCERT-aligned lessonscohortsid, name, program\_id, mentor\_user\_id, start\_date60 cohorts mapped to mentorsenrollmentsid, student\_user\_id, cohort\_id, status, enrolled\_at3,000 enrollments (active/churned/paused/cancelled)subscriptionsid, student\_user\_id, payer\_user\_id, program\_id, statusNOTE: uses student\_user\_id not user\_idpaymentsid, subscription\_id, amount\_inr, status (captured/failed)3,541 payments \= ₹6.81 Cr capturedattendanceid, student\_user\_id, session\_id, present, attended\_at70,891 recordsassessmentsid, student\_user\_id, lesson\_id, score, max\_score, submitted\_at33,498 recordseventsid, student\_user\_id, event\_type, event\_data (JSONB), occurred\_at1,470,075 behavioral eventsinterventionsid, student\_user\_id, mentor\_user\_id, type, outcome, created\_at200 historical interventions, 54.95% success rate  
Feature Views (Materialized)  
ViewPurposev\_student\_featuresPer-student engagement, learning, assessment, risk metricsv\_daily\_engagementDaily aggregate of platform activityv\_cohort\_retentionWeekly retention % per cohortv\_at\_risk\_studentsStudents with risk\_tier IN ('urgent','critical')  
Important Schema Quirks (Easy to Trip On)

subscriptions uses student\_user\_id and payer\_user\_id, NOT user\_id  
programs table does NOT have description or features columns (those were removed) — they're hardcoded in frontend  
JSONB casts must be CAST(:param AS jsonb), NOT :param::jsonb (Pydantic v2 parser issue)  
cur.rowcount is unreliable with psycopg2.extras.execute\_values — must verify table count delta  
NUMERIC(4,2) overflows beyond 99.9 — caps required in simulator

9\. API DOCUMENTATION  
Base URL: http://localhost:8000 (dev)  
Auth: Bearer JWT in Authorization header (except /api/auth/\* and /api/health/\*)  
Auth Endpoints  
MethodRoutePurposeBodyAuthPOST/api/auth/loginJSON login{email, password}NonePOST/api/auth/tokenOAuth2 form login (Swagger)form: username/passwordNoneGET/api/auth/meCurrent user info—Bearer  
Health Endpoints  
MethodRoutePurposeGET/api/healthAPI livenessGET/api/health/dbDB connectivity check  
Student Endpoints (role: student)  
MethodRoutePurposeGET/api/students/me/dashboardFull student dashboardGET/api/students/me/streakEngagement streakGET/api/students/me/recommended-lessonsPersonalized lesson recsGET/api/students/me/weak-chaptersChapters needing focusPOST/api/students/lessons/{lesson\_id}/track-eventTrack lesson interaction  
Parent Endpoints (role: parent)  
MethodRoutePurposeGET/api/parents/me/childrenList child usersGET/api/parents/children/{student\_id}/dashboardChild-specific dashboard  
Mentor Endpoints (role: mentor)  
MethodRoutePurposeGET/api/mentors/me/cohortsMentor's assigned cohortsGET/api/mentors/me/at-risk-studentsAt-risk queueGET/api/mentors/students/{student\_id}/whisperWhisper Layer insights for one studentPOST/api/mentors/interventionsCreate intervention recordGET/api/mentors/me/interventionsMentor's intervention history  
Admin Endpoints (role: admin)  
MethodRoutePurposeGET/api/admin/overviewInstitute-wide KPIsGET/api/admin/cohorts/retentionCohort retention curvesGET/api/admin/revenueRevenue analyticsGET/api/admin/interventions/effectivenessIntervention success rates  
Course Endpoints (any authenticated role)  
MethodRoutePurposeGET/api/courses/programsList programs (still returns DB B2C plans)GET/api/courses/programs/{slug}Single program detailGET/api/courses/subjectsList subjectsGET/api/courses/subjects/{slug}/chaptersChapters in a subjectGET/api/courses/lessonsList lessonsGET/api/courses/lessons/{lesson\_id}Lesson detail  
Analytics Endpoints (role: admin OR mentor)  
MethodRoutePurposeGET/api/admin/analytics/engagement-trendDaily engagement over timeGET/api/admin/analytics/funnelSignup → enroll → active funnelGET/api/admin/analytics/churn-reasons5-bucket churn reason breakdownGET/api/admin/analytics/payment-healthPayment success/failure ratesGET/api/admin/analytics/cohorts/{cohort\_id}/deep-diveComprehensive cohort report  
Sample verified response — Cohort Deep Dive (NEET-2028 Delhi Alpha):  
json{  
  "cohort\_id": "4c683ca8-7e75-4a46-9161-843592ad41e4",  
  "cohort\_name": "NEET-2028 2028 Delhi Alpha",  
  "program\_name": "Mastermind",  
  "mentor\_name": "Sumit Pal",  
  "total\_students": 31,  
  "active\_count": 23,  
  "churned\_count": 8,  
  "avg\_login\_count": 61.87,  
  "avg\_lesson\_completion\_rate": 0.7128,  
  "avg\_attendance\_rate": 0.8979,  
  "avg\_score\_pct": 55.39,  
  "total\_revenue\_inr": 1524969.49,  
  "payment\_success\_rate": 100,  
  "students\_at\_risk": 23,  
  "week\_1\_retention": 100,  
  "week\_4\_retention": 100,  
  "week\_12\_retention": 90.32  
}

10\. AI/LLM INTEGRATIONS  
Currently Implemented  
None — all "AI" features so far are rules-based, intentionally:

Whisper Layer \= pattern matching on 47 signals  
Risk scoring \= weighted feature aggregation from feature views  
Lesson recommender \= weak chapter overlap

Planned (Days 17–25)  
Days 17–19: Sentinel Engine — Real ML

XGBoost classifier trained on v\_student\_features to predict 14-day churn  
SHAP for explainable risk scores  
lifelines library for Cox proportional hazards survival analysis  
DiCE for counterfactual "what would save this student" recommendations

Days 20–23: Tara AI Tutor

LLM: OpenAI GPT-4 or Anthropic Claude API (TBD)  
Vector DB: ChromaDB (local, embedded — Postgres pgvector as fallback)  
RAG corpus: NCERT textbook chapters (Physics/Chemistry/Bio/Math) \+ PYQs \+ JEET notes  
3 personality modes user-selectable:

Saathi — warm friend, Hinglish-friendly, motivational  
Strategist — exam-focused, time/score optimization, English-leaning  
Guru — deep concept explanations, analogy-heavy

Analogy Engine — 80+ pre-built Indian-context analogies mapped to NCERT chapters

Examples: Electrostatics \= hostel gossip propagation, Thermodynamics \= pressure cooker, Chemical equilibrium \= chai stall traffic

Memory layer — lightweight: weak chapters, last 10 doubts, mastered concepts, preferred mode  
Frustration detection — rules-based (repeated questions, short angry-toned messages, abandoned sessions → trigger mentor handoff)

Build vs Defer Scope  
BUILD (working code): Concept explainer, RAG, 3 modes, memory, frustration detection, LLM-enhanced Whisper Layer  
DEFER (documented only): Multi-modal image input, voice mode, auto personality switching, long-term vector memory, agentic proactive nudges, gamification, renewal prediction. Goes to docs/product/ai-tutor-vision-roadmap.md.  
Token / Cost Concerns

ChromaDB local \= $0 vector ops  
LLM API costs to be capped at \~$0.50/student/month for production budget  
Streaming responses required for tutor UX (don't make students wait)

11\. BUGS & ISSUES  
Resolved Bugs (Documented Lessons)  
\#BugRoot CauseFix1ON CONFLICT silent failuresPostgres treated upsert as success even with no row affectedAdded loud RuntimeError \+ verification count2Random email/phone collisions at scaleFaker generated duplicates at 5,622-user volumeDeterministic process-wide counters3cur.rowcount unreliable with execute\_valuespsycopg2 limitationVerify via SELECT COUNT(\*) delta4NUMERIC(4,2) overflowScore values exceeded 99.9Capped at 99.9 in simulator5Bcrypt hash hardcoded wrongWrong algorithm versionGenerate at runtime via \_pwd\_ctx.hash("demo123\!")6Swagger OAuth2 incompatible with JSON loginFastAPI Security expects form-urlencodedAdded separate /api/auth/token form endpoint alongside JSON /api/auth/login7Programs table column mismatchdescription/features columns removedRemoved from SELECT, hardcoded in frontend8JSONB cast syntaxPydantic v2 parser interpreted ::jsonbUse CAST(:edata AS jsonb)9Subscriptions column name confusionTable uses student\_user\_id not user\_idDocumented explicitly, fixed in cohort deep-dive query10Cohort deep-dive mega-query 500'dSingle 7-join query timed out / had bad referencesDecomposed into 7 step queries11Empty Logo.tsx file → "Element type is invalid"touch created file but paste went to wrong locationUsed cat \> file \<\< 'EOF' heredoc to write atomically12Tara originally named "Drishti"Conflict with Drishti IAS coaching brandRenamed to Tara (star/saviour, 4 letters, ownable)13Pragya/Vidya/Bodhi all taken in EdTechWeb search confirmed brand collisionsChose Tara (clearest)  
Current Limitations

No real ML model yet (all churn predictions are rules-based)  
No actual LLM connection yet (Whisper Layer is template-based)  
No mobile testing done  
No automated tests written  
No CI/CD pipeline

Known Quirks

npm shows engine warning mute-stream@4.0.0 requires node ^22.x — harmless, ignore  
Tailwind v4 syntax differs from v3 — uses @theme inline block instead of config file  
Next.js 16 telemetry prompt appears on first run — user already declined

12\. IMPORTANT DECISIONS TAKEN  
Strategic / Product Decisions  
DecisionWhyPivot from B2C EdTech brand to B2B SaaSB2C market saturated (Allen/PW/Vedantu/BYJU's). B2B has near-zero competition in India. Data already built supports B2B (cohorts, mentors, admin views). Better VC narrative. Better IIMA capstone defense.Position as "Retention OS""OS" is VC-coded language (Linear, Notion). Frames JEET as infrastructure, not a feature.Hardcode B2B pricing in frontend, not DBDB plans are B2C student tiers. Don't pollute DB with B2B until enterprise sales process exists.Avoid naming competitors (Allen/Aakash/PW) by nameLegal grey zone for early-stage product. Use generic "Coaching A / Coaching B" in marketing.Founder is solo, no IIMA EPAIB capstone tag visibleTreat as real startup, not academic project. IIM-A appears only in credentials line.Remove Lucknow from messagingDon't anchor brand to a single city — positions as national platform.  
Technical Decisions  
DecisionWhyPostgreSQL over MongoDBRelational structure fits cohort/enrollment/payment relationships. JSONB columns cover flex data.FastAPI over DjangoModern async-ready, auto Swagger docs, Pydantic validation, lighter than Django for API-only backend.SQLAlchemy Core (not ORM) for analytics queriesDirect SQL is easier to optimize for complex analytics; ORM would obscure performance.Synthetic data first, not real users1.47M event simulation lets ML training begin before any institute signs up.Step-decomposed SQL queries over mega-joinsEasier to debug, easier for non-experts to maintain, performance often similar with proper indexing.Next.js 16 App Router over Pages RouterModern Next.js. Server Components by default. Recruiters look for App Router experience.shadcn/ui over MUI/ChakraComponents copied into repo \= full ownership, no lock-in. Industry standard for modern SaaS.Tailwind v4 over v3Latest stable, simpler config via CSS variables.Custom inline SVG components over Figma exportsLogo \+ Hero illustration are React components with props, easier to maintain than imported PNG/SVG files.  
Brand Decisions  
DecisionWhyLogo: Signal Waves (chosen from 6 directions)Most "infrastructure SaaS" feel. Says "we detect, we predict" without being literal. Reads as Datadog/Segment energy.AI Tutor name: Tara (replaces Drishti)Means "star/saviour", 4 letters, no Indian EdTech conflict.Hero illustration: Coaching A → student → JEET layer → Coaching BSingle image tells the entire product story. Demo opener.Bilingual chorus in DevanagariAuthentic founder voice. "हर स्टूडेंट टिकता है। हर इंस्टीट्यूट जीतता है।" uses spoken Hindi forms not purist Sanskrit.Founder bio Variant A (confident, founder-market-fit framing)"Spent years inside Indian EdTech... watching institutes hemorrhage LTV... building JEET to fix it" — establishes credibility, shows problem origin, ends with credentials.Color palette: Indigo \+ Orange \+ Midnight \+ BoneIndigo \= trust/intelligence (Stripe/Linear/Notion). Orange \= action/warmth. Midnight \= text. Bone \= backgrounds.

13\. DESIGN REFERENCES & INSPIRATIONS  
Brand / Visual References

Linear — confident calm, indigo primary, sparse layouts, founder-friendly  
Stripe — confident headlines, clean typography hierarchy  
Notion — soft gradients, premium-without-flashy  
Razorpay — Indian SaaS that built credibility through clarity  
Datadog — "signal" / monitoring metaphors in marketing visuals

Anti-References (What JEET Should NOT Be)

BYJU'S — cartoonish, child-skewed  
Coursera — corporate-sterile, MOOC vibe  
Most Indian EdTech homepages — busy, motivational-poster style, too many CTAs

Typography

Inter (UI body) — Vercel/Linear default  
Lora (display headlines) — adds editorial warmth to keep JEET from feeling cold  
Hind (Devanagari) — gold standard for Hindi-English bilingual UI

Competitor Landscape (Documented)

B2C EdTech (intentionally NOT competing): Allen, Aakash, PhysicsWallah, Vedantu, BYJU's, Unacademy, FIITJEE, Resonance, Motion  
Global B2B retention SaaS (closest analogs): Civitas Learning, Othot, Mainstay  
Indian B2B competitors: Effectively none — category creation

14\. DEPLOYMENT & DEVOPS  
Current State

All local. Nothing deployed. No production environment.

Planned Deployment (Days 26–28)  
LayerServiceReasonFrontendVercelNative Next.js, free tier, auto-deploy from GitHubBackendRailwaySimple FastAPI deployment, free tierProduction DBSupabase (managed PostgreSQL)Free tier, easy migration from localDomainTBD (likely jeet.ai or jeet.app)Need to check availability  
Security Considerations

Currently: JWT\_SECRET\_KEY in .env (gitignored), passwords bcrypt-hashed, CORS restricted to localhost  
Production: Will need:

HTTPS via Vercel/Railway auto-TLS  
Environment variable management in hosting platform  
Rate limiting (planned: slowapi)  
Input sanitization audit  
SQL injection prevention (already mostly handled via SQLAlchemy params)  
Sentry or similar for error tracking

CI/CD

None yet. Day 26–28 will add GitHub Actions for:

Frontend: lint \+ build on PR  
Backend: pytest (when tests exist) \+ deploy on merge to main

GitHub Repo

URL: https://github.com/mukesh-ai-codes/jeet  
Branch: main (single branch workflow for solo dev)  
Commits: Day-by-day commit pattern (feat(api): ..., feat(frontend): ...)  
Last commit pending: Day 11 B2B rebrand \+ Devanagari \+ founder card

15\. NEXT STEP ROADMAP  
Immediate (Right After Reading This Doc)

Verify Day 11 visual completion — Confirm Devanagari renders correctly, founder card displays with photo, no console errors  
Commit Day 11:

bash   cd \~/Projects/jeet  
   git add frontend/  
   git commit \-m "feat(frontend): B2B rebrand — logo, hero illustration, founder card, Devanagari chorus"  
   git push origin main  
Day 12 — Auth Flow \+ Onboarding (NEXT MAJOR WORK)  
Files to create:

src/app/login/page.tsx — Email/password form  
src/app/onboarding/page.tsx — 8-question adaptive wizard  
src/lib/auth.ts — Auth context provider, useAuth hook  
src/components/auth/LoginForm.tsx  
src/components/auth/ProtectedRoute.tsx  
Update src/app/layout.tsx to wrap children in AuthProvider

Logic to implement:

Login form posts to /api/auth/login  
On success, store JWT in localStorage via setToken() (already in api.ts)  
Decode JWT to get user role → redirect to role-specific dashboard  
Protected route wrapper checks token \+ role on mount  
Onboarding wizard: 8 questions covering target exam, grade, weak subjects, study hours, motivation level, parent involvement, learning style, current institute  
Submit onboarding data → updates user\_profile

Days 13–16 — Dashboards

Day 13: Student dashboard at /student consuming /api/students/me/dashboard  
Day 14: Parent dashboard at /parent consuming /api/parents/children/{id}/dashboard  
Day 15: Mentor Coach Console at /mentor \+ Admin Command Center at /admin  
Day 16: Mobile responsive sweep \+ dark mode toggle \+ framer-motion animations

Days 17–19 — ML Pipeline (Sentinel Engine)

Export v\_student\_features to pandas DataFrame  
Train XGBoost binary classifier (target: churned within 14 days)  
Generate SHAP values for each prediction  
Fit Cox proportional hazards model with lifelines  
Generate DiCE counterfactuals  
Save models as pickle files  
Add /api/ml/predict-churn endpoint that loads model and returns prediction \+ SHAP

Days 20–23 — Tara AI Tutor

Set up ChromaDB instance  
Ingest NCERT chapters as embeddings  
Build retrieval endpoint  
Wire up LLM API (Anthropic Claude — given Mukesh is building on Claude)  
Implement 3 modes via system prompts  
Build analogy library (80+ entries) as a JSON/Python dict  
Add conversation memory (last 10 exchanges in Redis or Postgres)  
Rules-based frustration detection  
Tara chat UI in frontend at /tara

Days 24–25 — Pulse Interventions

A/B testing framework — randomize intervention message to \~50/50 cohort split  
Track outcome via existing interventions table  
Auto-trigger logic on at-risk threshold breach  
WhatsApp/SMS integration (Twilio sandbox initially)

Days 26–28 — Launch

Vercel deploy frontend (connect GitHub, set env vars)  
Railway deploy backend  
Supabase migrate database (run schema \+ import data)  
README.md expansion with screenshots  
Architecture diagram  
60-second demo video (Loom or similar)  
LinkedIn launch post draft

16\. CRITICAL CONTEXT TO REMEMBER  
About the Founder

Name: Mukesh Jain (also "Mukesh J" in terminal prompts)  
Background: IIM Ahmedabad EPAIB alum, NIT Jaipur (engineering)  
Industry experience: VP and Product Head roles in Indian EdTech  
Coding experience: ZERO prior coding background before this 28-day sprint  
Time commitment: Willing to do 12–16 hour days  
Machine: MacBook Air M3, macOS 26.3  
GitHub: mukesh-ai-codes  
Current sprint pace: Comfortably ahead of plan

Mentorship Style Requested  
The user explicitly asked for:

Concise, high-signal responses (no waffle)  
Founder-level product thinking (challenge weak assumptions, not just execute)  
Paste-able full file replacements when changing code (not "edit line 47 of file X")  
Step-by-step instructions when introducing new concepts (because zero prior coding background)  
AI Tutor priority for own learning: Explain complex concepts in funny analogies with Indian context  
Strategic framing before tactical execution (decision before code)  
Document mistakes as lessons in a learnable way

Communication Conventions Used in This Project

Day-by-day milestone framing ("Day 11 — landing page live")  
Emoji section headers for visual scanning (🎯 📐 🚀 ✅)  
Always end with explicit "Your Action" list  
Always offer "Reply with X to continue" prompts  
Reality check pace at major phase transitions (suggest sleep/breaks)  
Master Plan Update tables periodically to show progress

Coding Style Expectations

Python: Type hints encouraged, docstrings on functions, no over-engineering  
TypeScript: Strict mode, interfaces over types where possible  
SQL: Decomposed step queries over mega-joins; verify with COUNT(\*) after writes  
Comments: Explain WHY, not WHAT  
Naming: Descriptive, no abbreviations except common (id, db, url)

Things to NEVER Do (Hard Rules)

NEVER name competitors (Allen/Aakash/PhysicsWallah/BYJU's/Unacademy/Vedantu/FIITJEE) in marketing copy or product  
NEVER reference Lucknow in brand messaging  
NEVER tag this as IIMA EPAIB capstone in public-facing copy  
NEVER use "Drishti" for the AI tutor (use Tara)  
NEVER skip the "verify backend is running" check before frontend work  
NEVER assume the user can fix a frontend error solo — always offer to diagnose

Project Aesthetic Standard

Premium SaaS, not flashy EdTech — think Linear meets Razorpay  
Confident voice, not motivational poster  
Indian roots without being preachy — Devanagari chorus, not Sanskrit shlokas  
Founder honesty over marketing hype — every claim must trace to a real backend metric