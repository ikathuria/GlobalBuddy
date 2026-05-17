# Globalदोस्त (GlobalBuddy)

> A graph-powered community platform that helps international students settle into a US city, discover local culture, make friends, and eventually mentor future arrivals — a lifelong companion for the immigrant journey.

---

## Viability Summary

| | |
|---|---|
| **Market** | Clear gap — no platform combines graph-ranked community matching with AI-guided settlement and a mentor lifecycle for international students |
| **Feasibility** | Medium — graph intelligence and AI synthesis are built; platform expansion (auth, social, content) is well-understood engineering |
| **Free to build** | Mostly — all services have generous free tiers for development; Supabase Pro ($25/mo) needed before production launch |
| **Monetization** | B2B: university international student office SaaS; B2C: freemium with premium mentor access |

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Frontend | React 18 + Vite + React Router | Already built; React Router adds multi-page routing without full Next.js migration |
| Backend | FastAPI (Python) | Already built; owns AI/graph intelligence; async, clean Pydantic contracts |
| Graph DB | Neo4j AuraDB free | Social graph, mentor/peer/resource matching; 200k nodes / 400k relationships free |
| Relational DB | Supabase Postgres | User accounts, content, settings — 500MB free, pairs with Auth + Realtime |
| Auth | Supabase Auth | 50k MAU free; email + LinkedIn OAuth; session management built-in |
| Realtime | Supabase Realtime | Online presence, live notifications; 200 concurrent connections free |
| Storage | Supabase Storage | Profile photos, content media; 1GB free |
| Cache | Upstash Redis | Session cache, rate limiting; free tier sufficient for dev |
| AI (primary) | Gemini 2.5 Flash | 1,500 req/day + 1M tokens/min free — 166× more generous than alternatives |
| AI (fast fallback) | Groq (Llama 3) | Sub-200ms responses; free tier for lightweight queries (cultural bridge, chat) |
| Maps | Leaflet + OpenStreetMap | 100% free, no API key, replaces Google Maps links with real embedded maps |
| Email | Resend | 3k free emails/month; intro requests, welcome emails, notifications |
| Hosting (frontend) | Vercel | Free tier; zero-config React/Vite deploy |
| Hosting (backend) | Railway | $5 free credit/month for FastAPI; simple env var management |

> **Note on Supabase free tier:** Projects pause after 1 week of inactivity. Fine for development. Upgrade to Supabase Pro ($25/mo) before public launch to prevent downtime.

---

## Environment Variables

```
# Backend (.env)
NEO4J_URI=                  # neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=             # neo4j
NEO4J_PASSWORD=             # AuraDB password

GEMINI_API_KEY=             # https://aistudio.google.com/app/apikey
GROQ_API_KEY=               # https://console.groq.com (free, no card)
ANTHROPIC_API_KEY=          # Optional paid fallback

SUPABASE_URL=               # https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=  # Supabase project settings → API → service_role key
SUPABASE_JWT_SECRET=        # Supabase project settings → API → JWT secret

UPSTASH_REDIS_URL=          # Upstash console → Redis → REST URL
UPSTASH_REDIS_TOKEN=        # Upstash console → Redis → REST token

RESEND_API_KEY=             # https://resend.com/api-keys (free)

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=         # https://developer.linkedin.com
LINKEDIN_CLIENT_SECRET=     # LinkedIn Developer App secret
LINKEDIN_REDIRECT_URI=      # e.g. http://localhost:8000/v1/auth/linkedin/callback

# Frontend (.env.local)
VITE_API_BASE_URL=          # http://localhost:8000 in dev; backend URL in prod
VITE_SUPABASE_URL=          # Same as SUPABASE_URL
VITE_SUPABASE_ANON_KEY=     # Supabase project settings → API → anon/public key
```

---

## Milestones

### Milestone 1: Scaffold ✅
**Goal:** Repo runs locally, folder structure in place, all dependencies installed.

Tasks:
- [x] Initialize React + Vite frontend — Done when: `npm run dev` starts on port 5173
- [x] Initialize FastAPI backend — Done when: `uvicorn app.main:app` starts on port 8000
- [x] Set up folder structure (routers, agents, services/ai, db, utils) — Done when: all dirs exist
- [x] Configure `.env.example` with required variables — Done when: file committed

---

### Milestone 2: Core Onboarding Feature ✅
**Goal:** Profile → Plan → Explore flow works end-to-end with deterministic fallback.

Tasks:
- [x] `POST /v1/profile/match` — Neo4j matching with mentor/peer/local entity scoring
- [x] `POST /v1/plan/generate` — AI plan with topological task ordering and week grouping
- [x] `POST /v1/bridge/explain` — Cultural term explanation with home-country analogy
- [x] `GET /v1/graph/subgraph` — Session-scoped Neo4j subgraph for vis-network
- [x] Deterministic fallback for plan and bridge when AI unavailable

---

### Milestone 3: Core UI/UX ✅
**Goal:** A real user can complete all 3 onboarding steps without confusion.

Tasks:
- [x] Step 1: 3-section profile wizard (personal, origin, destination)
- [x] Step 2: 30-day plan timeline with week grouping and task completion tracking
- [x] Step 3: Explore workspace with category filter chips and vis-network graph canvas
- [x] Cultural Bridge drawer with quick chips and term lookup
- [x] Person profile modal with contact links (email, LinkedIn, Instagram, phone)
- [x] Node detail card with Maps handoff
- [x] Health status panel (API + Neo4j)

---

### Milestone 4: Auth & Persistent Accounts
**Goal:** Users have real accounts; their profile, plan progress, and connections persist across sessions and devices.

Tasks:
- [ ] Add `supabase-py` to `backend/requirements.txt` and `@supabase/supabase-js` to `frontend/package.json` — Done when: both install without errors
- [ ] Create Supabase project and configure Auth with email/password + magic link — Done when: Supabase dashboard shows Auth enabled
- [ ] Add `POST /v1/auth/signup` and `POST /v1/auth/login` FastAPI endpoints that delegate to Supabase Auth and return a JWT — Done when: curl signup creates a Supabase user and returns a token
- [ ] Add JWT verification middleware to FastAPI — all `/v1/*` routes except health and auth require a valid Supabase JWT — Done when: unauthenticated request to `/v1/profile/match` returns 401
- [ ] Create Supabase Postgres tables: `user_profiles` (id, supabase_uid, full_name, email, country_of_origin, target_university, target_city, stage, created_at), `plan_progress` (user_id, task_id, completed, updated_at) — Done when: migrations run via `supabase db push`
- [ ] Add `react-router-dom` to frontend and define routes: `/` (landing), `/onboarding` (Steps 1-3), `/dashboard` (logged-in home), `/profile/:id` (public profile) — Done when: navigating to each path renders the correct component without 404
- [ ] Add login/signup page at `/auth` with email form — Done when: signing up creates an account and redirects to `/onboarding`
- [ ] Migrate plan task completion from localStorage to `plan_progress` Supabase table — Done when: completing a task on one device reflects on another after refresh

---

### Milestone 5: LinkedIn OAuth
**Goal:** Users can sign in and pre-fill their profile with LinkedIn data in one click.

Tasks:
- [ ] Register LinkedIn Developer App with scopes `openid`, `profile`, `email` — Done when: Client ID and Secret available in `.env`
- [ ] Enable LinkedIn as OAuth provider in Supabase Auth dashboard — Done when: LinkedIn appears under Auth → Providers
- [ ] Add "Continue with LinkedIn" button to the auth page (`/auth`) that triggers Supabase OAuth flow — Done when: clicking the button redirects to LinkedIn and returns a logged-in session
- [ ] Add `GET /v1/auth/linkedin/profile` endpoint that uses the LinkedIn access token from the Supabase session to call `/v2/userinfo` and return mapped fields `{full_name, email, linkedin_url, country_of_origin, target_university}` — Done when: endpoint returns pre-fill data for a logged-in LinkedIn user
- [ ] Update `ProfileForm.jsx` to call the pre-fill endpoint on mount if the user authenticated via LinkedIn — pre-fills empty fields only, marks imported fields visually — Done when: LinkedIn-authed users land on Step 1 with fields pre-populated

---

### Milestone 6: Reliability Hardening
**Goal:** Logs, error telemetry, and tests make failure visible and recoverable in production.

Tasks:
- [x] Add structured JSON logging to AI agents — `ai_event=` log lines with provider name, latency_ms, and fallback flag in `judge_agent.py` and `cultural_bridge_agent.py`
- [x] Add request-level timeout middleware to `/v1/plan` and `/v1/bridge` — `_RequestTelemetryMiddleware` in `main.py` logs elapsed_ms; AI calls wrapped with `asyncio.wait_for(timeout=AI_TIMEOUT_SECONDS)` with explicit `asyncio.TimeoutError` handling and fallback
- [x] Add `GET /health/providers` endpoint that pings Gemini, Groq, and Anthropic — returns `{status, latency_ms}` per provider; `not_configured` when key absent
- [x] Write regression tests for `new_to_us=False` skip behavior — `tests/test_new_to_us.py` (5 tests, all passing)
- [x] Write smoke tests for the full 3-step flow using mock Neo4j responses — `tests/test_smoke.py` (13 tests covering profile→plan→bridge→graph + AI timeout fallback paths, all passing)
- [ ] Replace in-memory session store with Upstash Redis-backed store, TTL 24h — Done when: session survives `uvicorn` restart (requires UPSTASH_REDIS_URL)

---

### Milestone 7: User Lifecycle & Journey Stages
**Goal:** Users progress through defined stages (Newcomer → Settler → Local → Mentor); the platform surfaces different content and connections at each stage.

Tasks:
- [ ] Define `stage` enum in `user_profiles` Supabase table: `newcomer` (0–3 months), `settler` (3–12 months), `local` (1–2 years), `mentor` (opted in) — Done when: migration applied and `stage` column exists
- [ ] Add stage detection logic in `profile_match_agent.py` — infer stage from `arrival_date` if provided, default to `newcomer` — Done when: profile match response includes `user_stage` field
- [ ] Update Neo4j matching weights per stage — newcomers get more mentor matches; settlers get more peer/social matches; locals get more community/event matches — Done when: stage=`settler` returns proportionally more peer matches than stage=`newcomer`
- [ ] Add stage progress indicator to the frontend dashboard — visual journey bar showing current stage and what unlocks next — Done when: dashboard shows "You're a Settler — 3 more months to Local" style progress
- [ ] Add "Upgrade my stage" prompt — after 90 days as newcomer, show a banner inviting the user to mark themselves as settled — Done when: banner appears at 90-day mark and updates `stage` on confirm

---

### Milestone 8: Pre-Arrival Checklist & Document Tracker
**Goal:** Students can prepare before landing and track critical first-month documents.

Tasks:
- [ ] Add `PreArrivalChecklist` node type to Neo4j seed data with ~15 items (book temporary housing, get international SIM, carry printed I-20, notify bank of travel, download offline maps, arrange airport pickup) — Done when: nodes exist in graph with `category: pre_arrival`
- [ ] Add `/pre-arrival` route and `PreArrivalPanel.jsx` component — a checklist page accessible before Step 1 (no auth required) — Done when: visiting `/pre-arrival` shows an interactive checklist
- [ ] Add `DocumentTracker` component to the dashboard — tracks SSN, bank account, student ID, health insurance, I-20 copy, lease with status (pending / in-progress / done) and links to how-to guides — Done when: each document item has a status toggle and an info drawer
- [ ] Persist document tracker state to Supabase `user_documents` table (user_id, doc_type, status, updated_at) — Done when: document status persists across sessions
- [ ] Add `Task` graph nodes for each document (SSN, bank, health insurance) linked to the plan's topological order — Done when: plan generation includes document tasks in the correct sequence

---

### Milestone 9: Persistent AI Chat
**Goal:** The Cultural Bridge becomes a full persistent chat assistant — students can ask anything about US life, their city, or their situation.

Tasks:
- [ ] Add `chat_messages` table to Supabase Postgres: `{id, user_id, role (user/assistant), content, created_at}` — Done when: migration applied
- [ ] Add `POST /v1/chat/message` FastAPI endpoint — accepts `{message, session_id}`, loads last 10 messages for context, calls Gemini/Groq, stores both user message and response, returns assistant reply — Done when: sending two consecutive messages returns a contextually aware second response
- [ ] Create `ChatPanel.jsx` — a persistent chat interface accessible from the dashboard sidebar; shows message history, typing indicator, and quick-chip suggestions (SSN, credit score, bank account, lease) — Done when: chat renders history on mount and appends new messages in real-time
- [ ] Replace the existing `CulturalBridgeDrawer.jsx` one-off term lookup with a link that opens `ChatPanel` pre-seeded with the term as the first message — Done when: clicking a quick chip in the old drawer opens the full chat with the term as context
- [ ] Add Supabase Realtime subscription to `ChatPanel` so assistant responses stream into the UI as they arrive — Done when: assistant reply appears word-by-word without page refresh

---

### Milestone 10: Social Layer — Connections & Buddy System
**Goal:** Users can connect with each other, request mentor introductions, and build a real social graph on the platform.

Tasks:
- [ ] Add `connections` table to Supabase Postgres: `{id, requester_id, recipient_id, status (pending/accepted/declined), created_at}` — Done when: migration applied
- [ ] Add `POST /v1/social/connect` endpoint — sends a connection request; stores in Supabase and creates a `KNOWS` edge in Neo4j on acceptance — Done when: accepting a request creates the Neo4j edge and updates Supabase status
- [ ] Update person profile modal — add "Request Connection" button for peers and "Request Intro" button for mentors; both are disabled until the user is logged in — Done when: buttons appear on the modal and fire the correct endpoint
- [ ] Add `POST /v1/social/intro-request` endpoint — sends a templated intro email via Resend to the mentor (not exposing their raw email to the requester); email includes requester's name, university, country, and a one-click accept link — Done when: a test intro request sends an email to the mentor's address
- [ ] Add `/connections` dashboard page listing accepted connections with their stage, university, and country — Done when: page renders a card grid of the user's connections
- [ ] Add WhatsApp/Telegram group links as `CommunityGroup` nodes in Neo4j (by university + country of origin + city) — surface them in the Explore workspace under a new "Groups" filter chip — Done when: "Groups" chip in Step 3 shows relevant group cards with join links

---

### Milestone 11: Cultural & City Discovery Feed
**Goal:** Logged-in users see an ongoing feed of culturally relevant events, guides, and local tips — not tied to the 30-day clock.

Tasks:
- [ ] Add `content_items` table to Supabase Postgres: `{id, type (event/guide/tip), title, body, city, tags[], author_id, published_at}` — Done when: migration applied
- [ ] Seed 20+ content items for Chicago: cultural events, neighborhood guides, city tips (transit, tipping, seasons, healthcare system), restaurant spotlights by cuisine — Done when: `SELECT count(*) FROM content_items` returns ≥ 20
- [ ] Add `GET /v1/feed` FastAPI endpoint — returns content items filtered by user's `target_city` and `cultural_background` tags, sorted by relevance score — Done when: endpoint returns city-matched, culturally relevant items
- [ ] Add `FeedPage.jsx` at `/feed` route — card-based feed with category filter tabs (Events, Guides, Tips, Food) and infinite scroll (10 items per page) — Done when: scrolling past 10 items loads the next batch
- [ ] Replace Leaflet + OpenStreetMap for all location-based nodes — embed a real interactive map tile in `NodeDetailCard.jsx` and `MapPreviewPanel.jsx` instead of a Google Maps link — Done when: clicking a LocalEntity node shows an embedded Leaflet map centered on that location
- [ ] Add "Save" button to feed items — saved items stored in Supabase `saved_content` table and accessible at `/saved` — Done when: saved items persist across sessions

---

### Milestone 12: Mentor System
**Goal:** Settled users can opt in as mentors; newcomers get matched to them; mentors build a reputation over time.

Tasks:
- [ ] Add `mentor_profiles` table to Supabase Postgres: `{user_id, expertise[], availability, bio, response_rate, intro_count, rating, opted_in_at}` — Done when: migration applied
- [ ] Add `/become-mentor` page and flow — asks the user to set expertise areas, availability, and a short bio; requires `stage` = `settler`, `local`, or `mentor` — Done when: submitting the form sets `stage = mentor` in `user_profiles` and creates a `mentor_profiles` row
- [ ] Update `profile_match_agent.py` — include opted-in mentor profiles from Supabase in the Neo4j matching query; mentors with higher `intro_count` and `rating` get score bonus — Done when: opted-in mentors appear at the top of newcomer match results
- [ ] Add mentor rating flow — after a connection is marked accepted for 7 days, prompt the newcomer to rate the mentor (1–5 stars); store in `mentor_ratings` table and update `mentor_profiles.rating` — Done when: rating prompt appears in dashboard notifications after 7 days
- [ ] Add `/mentors` public directory page — lists opted-in mentors filterable by city, university, country of origin, expertise; each card links to their public profile — Done when: page renders with working filters and ≥ 1 seeded mentor per city

---

### Milestone 13: Notifications
**Goal:** Users receive timely, useful notifications — in-app and via email — without being spammed.

Tasks:
- [ ] Add `notifications` table to Supabase Postgres: `{id, user_id, type, title, body, read, created_at}` — Done when: migration applied
- [ ] Add notification triggers: connection request received, intro request accepted, new message, stage upgrade available, document tracker reminder (7 days after signup if SSN not marked done) — Done when: each trigger creates a row in `notifications`
- [ ] Add notification bell icon to the frontend nav — badge count from Supabase Realtime subscription; clicking opens a dropdown of recent notifications — Done when: receiving a test notification increments the badge without page refresh
- [ ] Add Resend email integration — send email for connection accepted, intro request received, and weekly digest (new mentors in your city, upcoming events) — Done when: test emails arrive with correct content and unsubscribe link
- [ ] Add browser push notification opt-in — use Web Push API; prompt user after first login — Done when: test push notification appears on desktop when the tab is closed

---

### Milestone 14: Multi-City Data Expansion
**Goal:** At least 3 cities have complete, verified graph data — Chicago (existing), Boston, and NYC.

Tasks:
- [ ] Audit Chicago seed data — verify all required node labels (Person/Mentor, University, Task, LocalEntity, Event, CommunityGroup) are present with required properties — Done when: `python -m app.db.validate_seed --city chicago` prints a clean quality report
- [ ] Add Boston seed pack (Northeastern, BU, MIT, Harvard) — mentors, local entities (grocery, worship, housing, transit), tasks, events, community groups — Done when: `POST /v1/profile/match` with `target_city: "Boston"` returns ≥ 5 mentors and ≥ 10 local entities
- [ ] Add NYC seed pack (NYU, Columbia, CUNY) — same coverage as Boston — Done when: `POST /v1/profile/match` with `target_city: "New York"` returns ≥ 5 mentors and ≥ 10 local entities
- [ ] Add city selector to `ProfileForm.jsx` Step 1 — dropdown of supported cities with "More cities coming soon" for unsupported entries — Done when: selecting a city from the dropdown sets `target_city` correctly
- [ ] Add metadata quality checks — warn if any LocalEntity node is missing `maps_url`, any Person node is missing `email`, any Task node is missing a `PRECEDES` edge — Done when: `validate_seed` script prints warnings for incomplete nodes

---

### Milestone 15: Deploy
**Goal:** Platform is live at a public URL; all services connected in production.

Tasks:
- [ ] Build frontend with `npm run build` and deploy `frontend/dist` to Vercel — Done when: public Vercel URL loads the app
- [ ] Deploy FastAPI backend to Railway with all env vars set via platform secrets — Done when: `GET /health` and `GET /health/neo4j` return `ok` at the Railway URL
- [ ] Upgrade Supabase project from free to Pro ($25/mo) to prevent auto-pausing — Done when: Supabase dashboard shows Pro plan active
- [ ] Set `VITE_API_BASE_URL` in Vercel environment to the Railway backend URL — Done when: frontend API calls succeed in production
- [ ] Configure custom domain (if available) on Vercel — Done when: app loads at the custom domain with HTTPS
- [ ] Smoke-test the full platform flow on production: signup → LinkedIn OAuth → onboarding → plan → explore → chat → connection request → feed — Done when: all steps complete without errors on the production URL
- [ ] Add `railway.toml` to repo root for reproducible backend deploys — Done when: `railway up` redeploys cleanly from CI

---

### Milestone 16: Polish
**Goal:** No obvious errors; loading states present; edge cases handled; branding consistent.

Tasks:
- [ ] Audit all UI copy for Globalदोस्त branding — zero product-facing "GlobalBuddy" strings in `frontend/src` — Done when: grep finds no product-facing instances
- [ ] Add loading skeletons to `PlanPanel.jsx`, `FeedPage.jsx`, and `ExploreWorkspace.jsx` — Done when: a 2-second artificial delay shows skeleton UI, not a blank panel
- [ ] Add React error boundary in `App.jsx` — catches unhandled errors and shows "Something went wrong, please refresh" — Done when: throwing inside any panel renders the fallback
- [ ] Ensure all API error states (Neo4j down, AI timeout, Supabase unreachable) surface a recoverable `Banner.jsx` — Done when: killing Neo4j locally shows a visible banner, not a silent blank
- [ ] Add verification disclaimer to all entity cards (LocalEntity, Event, mentor profiles) for non-live data — Done when: disclaimer text is visible on every card
- [ ] Accessibility audit — all interactive elements have ARIA labels, keyboard navigation works through the 3-step flow and dashboard — Done when: tab-key navigation completes all forms without a mouse

---

## Claude Code Commands

**Start at the first incomplete milestone:**
```
claude "Read PLAN.md and complete the first milestone that has unchecked tasks. Mark tasks done as you go. Stop after that milestone and commit."
```

**Resume from any point:**
```
claude "Read PLAN.md, find the first incomplete task, and continue. Mark tasks done as you go. Commit when a milestone is complete."
```

**Run a specific milestone:**
```
claude "Read PLAN.md and complete Milestone 4 (Auth & Persistent Accounts). Mark tasks done as you go. Stop after Milestone 4 and commit."
```

**Test current state:**
```
claude "Read PLAN.md. Without building anything new, test everything marked done. Run pytest for backend, check the platform flow in the browser. Report what works and what's broken."
```

---

## Notes & Decisions

- **Neo4j + Supabase split:** Neo4j owns relationship intelligence (matching, graph traversal, community detection). Supabase Postgres owns structured user/content data. Never duplicate user profile data — Neo4j `Person` nodes reference Supabase `user_id` as a property.
- **Auth token flow:** Supabase issues a JWT on login. The frontend sends it as `Authorization: Bearer <token>` on every API call. FastAPI verifies it using `SUPABASE_JWT_SECRET`. No custom auth logic needed.
- **Gemini vs Groq routing:** Use Gemini 2.5 Flash for plan generation and multi-turn chat (needs high token count). Use Groq for cultural bridge one-off lookups (needs low latency). The existing provider factory handles this — add a `prefer_speed` flag to the AI call.
- **Stage progression:** Stage is set by the backend based on `arrival_date`. Users can also manually advance their stage. Never let stage go backward automatically.
- **Mentor opt-in only:** Never auto-graduate a user to mentor. It must be an explicit opt-in action. Mentors can pause or deactivate their availability without losing their history.
- **LinkedIn OAuth scope:** Basic OIDC (`openid profile email`) works without app review. Education history endpoint requires LinkedIn review (1–4 weeks). Build pre-fill to work without education data and treat university pre-fill as a bonus.
- **Supabase free tier pausing:** For development, resume the project manually if it pauses. Do not upgrade to Pro until Milestone 15 (Deploy).
- **Branding:** Product-facing name is **Globalदोस्त**. Code identifiers use `globaldost` or `globalbuddy`. Only update UI copy strings, never rename code symbols.
- **Maps migration:** Replace all `maps.google.com` link-outs with Leaflet embedded maps using OpenStreetMap tiles. No API key required. Add `leaflet` and `react-leaflet` to `frontend/package.json`.
- **Email privacy:** Intro request emails are sent by the backend via Resend — the requester never sees the mentor's raw email address. The mentor's email is only in the backend environment.
