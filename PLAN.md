# Globalदोस्त (GlobalBuddy)

> A graph-powered community platform that helps international students settle into a US city, discover local culture, make friends, and eventually mentor future arrivals — a lifelong companion for the immigrant journey.

---

## Viability Summary

| | |
|---|---|
| **Market** | Clear gap — no platform combines graph-ranked community matching with AI-guided settlement and a mentor lifecycle for international students |
| **Feasibility** | Medium — graph intelligence and AI synthesis are built; next work is simplifying the data layer around Neon + Markdown |
| **Free to build** | Yes for MVP — Neon handles auth/Postgres, graph knowledge lives in Git-backed Markdown, and R2 is optional only when uploads are needed |
| **Monetization** | B2B: university international student office SaaS; B2C: freemium with premium mentor access |

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Frontend | React 18 + Vite + React Router | Already built; React Router adds multi-page routing without full Next.js migration |
| Backend | FastAPI (Python) | Already built; owns AI, graph indexing, ranking, and Pydantic contracts |
| Knowledge Graph | Markdown + YAML frontmatter + `[[wikilinks]]` | Obsidian-style graph stored in Git; free, editable, easy to validate and demo |
| Relational DB | Neon Postgres | User accounts, plan progress, chat, connections, feed, mentor profiles, notifications |
| Auth | Neon Auth | Managed auth synced into Neon Postgres; keeps auth + user data on one default platform |
| Realtime | Deferred; SSE/WebSocket when needed | Avoids provider-specific realtime dependency during MVP |
| Storage | Cloudflare R2, optional later | Profile photos and uploads only when product needs them |
| Cache | Upstash Redis | Session cache, rate limiting; free tier sufficient for dev |
| AI (primary) | Gemini 2.5 Flash | 1,500 req/day + 1M tokens/min free — 166× more generous than alternatives |
| AI (fast fallback) | Groq (Llama 3) | Sub-200ms responses; free tier for lightweight queries (cultural bridge, chat) |
| Maps | Leaflet + OpenStreetMap | 100% free, no API key, replaces Google Maps links with real embedded maps |
| Email | Resend | 3k free emails/month; intro requests, welcome emails, notifications |
| Hosting (frontend) | Vercel | Free tier; zero-config React/Vite deploy |
| Hosting (backend) | Railway | $5 free credit/month for FastAPI; simple env var management |

> **Data-layer decision:** Neo4j remains a useful future upgrade if the graph becomes highly dynamic or query-heavy. For the MVP, public city knowledge moves to Markdown so the app is cheaper, easier to edit, and not constrained by managed graph database limits. Supabase is no longer the default because project slots are the bottleneck across multiple active projects.

---

## Environment Variables

```
# Backend (.env)
DATABASE_URL=               # Neon pooled Postgres connection string
DATABASE_URL_UNPOOLED=      # Neon direct connection string, useful for migrations

# Neon Auth
NEON_AUTH_URL=              # Neon Auth service URL
NEON_AUTH_JWKS_URL=         # JWKS endpoint for backend JWT verification
NEON_AUTH_ISSUER=           # Optional expected JWT issuer
NEON_AUTH_AUDIENCE=         # Optional expected JWT audience
AUTH_REQUIRED=false         # Set true to require JWTs on protected /v1 routes

GEMINI_API_KEY=             # https://aistudio.google.com/app/apikey
GROQ_API_KEY=               # https://console.groq.com (free, no card)
ANTHROPIC_API_KEY=          # Optional paid fallback

UPSTASH_REDIS_URL=          # Upstash console → Redis → REST URL
UPSTASH_REDIS_TOKEN=        # Upstash console → Redis → REST token

RESEND_API_KEY=             # https://resend.com/api-keys (free)

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=         # https://developer.linkedin.com
LINKEDIN_CLIENT_SECRET=     # LinkedIn Developer App secret
LINKEDIN_REDIRECT_URI=      # e.g. http://localhost:8000/v1/auth/linkedin/callback

# Frontend (.env.local)
VITE_API_BASE_URL=          # http://localhost:8000 in dev; backend URL in prod
VITE_NEON_AUTH_URL=         # Neon Auth service URL for the Vite client
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
- [x] `POST /v1/profile/match` — graph matching with mentor/peer/local entity scoring (currently Neo4j-backed; Markdown graph migration planned)
- [x] `POST /v1/plan/generate` — AI plan with topological task ordering and week grouping
- [x] `POST /v1/bridge/explain` — Cultural term explanation with home-country analogy
- [x] `GET /v1/graph/subgraph` — session-scoped subgraph for vis-network
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
- [x] Health status panel (API + graph source)

---

### Milestone 4: Markdown Knowledge Graph Engine
**Goal:** Replace Neo4j as an MVP requirement with an Obsidian-style Markdown graph compiled into typed nodes, edges, evidence bundles, and subgraphs.

Tasks:
- [x] Define Markdown node schema: YAML frontmatter + body + `[[wikilinks]]` — Done when: docs describe required fields for `Mentor`, `Peer`, `University`, `Task`, `LocalEntity`, `Event`, `CommunityGroup`, and `Guide`
- [x] Create `data/graph/{city}/...` folder structure — Done when: Chicago has at least one validated node of each required type
- [x] Build parser for frontmatter, wikilinks, explicit relationships, and task dependencies — Done when: parser emits normalized `{nodes, edges}` without Neo4j
- [x] Add `MarkdownGraphService` with in-memory index and city/profile filtering — Done when: service can return mentors, peers, places, tasks, events, and groups for Chicago
- [x] Replace Neo4j reads in `profile_match_agent.py` and `graph_service.py` behind a graph adapter interface — Done when: `/v1/profile/match` works without `NEO4J_*` env vars
- [x] Update `/v1/graph/subgraph` and health UI for Markdown graph status — Done when: `/health/graph` returns node/edge counts and source=`markdown`
- [x] Add graph validation tests for duplicate IDs, broken wikilinks, missing required fields, and invalid task dependency cycles — Done when: validation fails clearly for bad fixtures
- [x] Keep Neo4j/Cypher files as optional legacy seed assets until migration is proven — Done when: README calls Neo4j optional, not required

---

### Milestone 5: Neon Auth & Persistent Accounts
**Goal:** Users have real accounts; profile, plan progress, documents, chat, and connections persist across sessions and devices in Neon Postgres.

Tasks:
- [x] Add Postgres migration tooling and driver (`asyncpg`/SQLAlchemy or equivalent) - Done when: `python -m app.db.migrate` can apply SQL migrations against Neon
- [x] Configure Neon project/Auth env contract - Done when: `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, `NEON_AUTH_URL`, and `NEON_AUTH_JWKS_URL` are documented in env examples; console values are supplied per deployment
- [x] Add Neon Auth frontend integration at `/auth` - Done when: email signup/login uses the Neon Auth SDK when `VITE_NEON_AUTH_URL` is set and redirects signup to onboarding
- [x] Add JWT verification middleware to FastAPI - Done when: protected `/v1/*` routes require a valid Neon Auth token when `AUTH_REQUIRED=true` and a JWKS URL is configured
- [x] Create Neon Postgres tables: `user_profiles`, `plan_progress`, `user_documents`, `chat_messages`, `connections`, `content_items`, `saved_content`, `mentor_profiles`, `mentor_ratings`, `notifications` - Done when: `backend/migrations/001_neon_persistence.sql` defines the schema
- [x] Link `user_profiles.auth_user_id` to Neon Auth's synced user row - Done when: `/v1/auth/me` and persistence routes resolve the app user profile from token claims
- [x] Add routes: `/` (onboarding), `/auth`, `/dashboard`, `/profile/:id`, `/chat`, `/pre-arrival` - Done when: each path renders without 404
- [x] Migrate plan task completion from localStorage to `plan_progress` - Done when: authenticated users sync progress through `/v1/progress/plan`, with localStorage fallback for no-auth demos

---

### Milestone 6: LinkedIn OAuth
**Goal:** Users can sign in and pre-fill their profile with LinkedIn data, using Neon Auth as the auth layer.

Tasks:
- [x] Register LinkedIn Developer App with scopes `openid`, `profile`, `email` — Done when: setup docs/env contract identify the required LinkedIn Client ID and Secret; actual console values are supplied per deployment
- [x] Configure LinkedIn as an OAuth provider in Neon Auth — Done when: `/auth` calls Neon Auth `signIn.social({ provider: "linkedin" })`; actual provider enablement happens in Neon console
- [x] Add "Continue with LinkedIn" button to `/auth` — Done when: clicking starts the Neon Auth LinkedIn OAuth redirect when `VITE_NEON_AUTH_URL` is configured
- [x] Add `GET /v1/auth/linkedin/profile` endpoint or token-claim mapper — Done when: backend returns `{source, full_name, email, linkedin_url, country_of_origin, target_university}` when available
- [x] Update `ProfileForm.jsx` to pre-fill empty fields for LinkedIn-authenticated users — Done when: imported account/LinkedIn fields are visually marked and never overwrite user-entered values

---

### Milestone 7: Reliability Hardening
**Goal:** Logs, error telemetry, graph validation, and tests make failure visible and recoverable in production.

Tasks:
- [x] Add structured JSON logging to AI agents — `ai_event=` log lines with provider name, latency_ms, and fallback flag in `judge_agent.py` and `cultural_bridge_agent.py`
- [x] Add request-level timeout middleware to `/v1/plan` and `/v1/bridge` — `_RequestTelemetryMiddleware` in `main.py` logs elapsed_ms; AI calls wrapped with `asyncio.wait_for(timeout=AI_TIMEOUT_SECONDS)` with explicit `asyncio.TimeoutError` handling and fallback
- [x] Add `GET /health/providers` endpoint that pings Gemini, Groq, and Anthropic — returns `{status, latency_ms}` per provider; `not_configured` when key absent
- [x] Write regression tests for `new_to_us=False` skip behavior — `tests/test_new_to_us.py` (5 tests, all passing)
- [x] Write smoke tests for the full 3-step flow using mock graph responses — `tests/test_smoke.py` covers profile→plan→bridge→graph + AI timeout fallback paths
- [x] Replace in-memory session store with Neon Postgres or Upstash Redis-backed store, TTL 24h — Done when: profile evidence/subgraph sessions persist in Neon `app_sessions` and rehydrate after process restart
- [x] Add Markdown graph validation to CI — Done when: `.github/workflows/ci.yml` runs `python -m app.db.validate_graph` before backend tests

---

### Milestone 8: User Lifecycle & Journey Stages
**Goal:** Users progress through defined stages (Newcomer → Settler → Local → Mentor); the platform surfaces different content and connections at each stage.

Tasks:
- [x] Define `stage` enum in Neon `user_profiles`: `newcomer` (0–3 months), `settler` (3–12 months), `local` (1–2 years), `mentor` (opted in) — Done when: migration applied and `stage` column exists
- [x] Add stage detection logic in `profile_match_agent.py` — infer stage from `arrival_date` if provided, default to `newcomer` — Done when: profile match response includes `user_stage` field
- [x] Update Markdown graph matching weights per stage — newcomers get more mentor/task matches; settlers get more peer/social matches; locals get more community/event matches
- [x] Add stage progress indicator to the frontend dashboard — Done when: dashboard shows "You're a Settler — 3 more months to Local" style progress
- [x] Add "Upgrade my stage" prompt — after 90 days as newcomer, show a banner inviting the user to mark themselves as settled

---

### Milestone 9: Pre-Arrival Checklist & Document Tracker
**Goal:** Students can prepare before landing and track critical first-month documents.

Tasks:
- [x] Add pre-arrival checklist content to existing graph seed data with ~15 items
- [x] Add `/pre-arrival` route and `PreArrivalPanel.jsx` component — a checklist page accessible before Step 1 (no auth required)
- [x] Add `DocumentTracker` component to the dashboard — tracks SSN, bank account, student ID, health insurance, I-20 copy, lease with status and links to how-to guides
- [ ] Convert pre-arrival checklist and document tasks to Markdown graph nodes — Done when: plan generation uses Markdown task dependencies
- [x] Persist document tracker state to Neon `user_documents` table — Done when: authenticated document status syncs through `/v1/documents`
- [x] Add `Task` graph nodes for each document (SSN, bank, health insurance) linked to the plan's topological order

---

### Milestone 10: Persistent AI Chat
**Goal:** The Cultural Bridge becomes a full persistent chat assistant — students can ask anything about US life, their city, or their situation.

Tasks:
- [x] Add `chat_messages` table to Neon Postgres: `{id, user_id, session_id, role (user/assistant), content, created_at}` — Done when: authenticated chat messages persist through `/v1/chat`
- [x] Add `POST /v1/chat/message` FastAPI endpoint — accepts `{message, session_id}`, loads last 10 messages for context, calls Gemini/Groq, stores both user message and response, returns assistant reply
- [x] Create `ChatPage.jsx` at `/chat` — persistent chat interface with message history, typing indicator, and quick-chip suggestions
- [ ] Replace the existing `CulturalBridgeDrawer.jsx` one-off term lookup with a link that opens `/chat` pre-seeded with the term as the first message
- [ ] Add SSE/WebSocket response streaming when needed — Done when: assistant reply appears incrementally without relying on provider-specific realtime

---

### Milestone 11: Social Layer — Connections & Buddy System
**Goal:** Users can connect with each other, request mentor introductions, and build a real social graph on the platform.

Tasks:
- [ ] Add `connections` table to Neon Postgres: `{id, requester_id, recipient_id, status (pending/accepted/declined), created_at}`
- [ ] Add `POST /v1/social/connect` endpoint — sends a connection request; stores dynamic user connections in Neon
- [ ] Update person profile modal — add "Request Connection" button for peers and "Request Intro" button for mentors; both disabled until the user is logged in
- [ ] Add `POST /v1/social/intro-request` endpoint — sends a templated intro email via Resend without exposing mentor email
- [ ] Add `/connections` dashboard page listing accepted connections with stage, university, and country
- [ ] Add WhatsApp/Telegram group links as Markdown `CommunityGroup` nodes — surface them in Explore under a new "Groups" filter chip

---

### Milestone 12: Cultural & City Discovery Feed
**Goal:** Logged-in users see an ongoing feed of culturally relevant events, guides, and local tips — not tied to the 30-day clock.

Tasks:
- [ ] Add `content_items` table to Neon Postgres for dynamic/published content
- [ ] Seed static Chicago guides, tips, and restaurant spotlights as Markdown `Guide` / `Event` / `LocalEntity` nodes
- [ ] Add `GET /v1/feed` FastAPI endpoint — returns Markdown graph items + Neon content filtered by city and cultural tags
- [ ] Add `FeedPage.jsx` at `/feed` route — card-based feed with category tabs and pagination/infinite scroll
- [ ] Replace Google Maps link-outs with Leaflet + OpenStreetMap embeds in `NodeDetailCard.jsx` and `MapPreviewPanel.jsx`
- [ ] Add "Save" button to feed items — saved items stored in Neon `saved_content` table and accessible at `/saved`

---

### Milestone 13: Mentor System
**Goal:** Settled users can opt in as mentors; newcomers get matched to them; mentors build a reputation over time.

Tasks:
- [ ] Add `mentor_profiles` table to Neon Postgres: `{user_id, expertise[], availability, bio, response_rate, intro_count, rating, opted_in_at}`
- [ ] Add `/become-mentor` page and flow — requires `stage` = `settler`, `local`, or `mentor`
- [ ] Merge opted-in Neon mentor profiles with Markdown seed mentors in `profile_match_agent.py`
- [ ] Add mentor rating flow — after an accepted connection is 7 days old, prompt newcomer to rate mentor and update `mentor_profiles.rating`
- [ ] Add `/mentors` public directory page — lists opted-in mentors filterable by city, university, country of origin, expertise

---

### Milestone 14: Notifications
**Goal:** Users receive timely, useful notifications — in-app and via email — without being spammed.

Tasks:
- [ ] Add `notifications` table to Neon Postgres: `{id, user_id, type, title, body, read, created_at}`
- [ ] Add notification triggers: connection request received, intro request accepted, new message, stage upgrade available, document tracker reminder
- [ ] Add notification bell icon to the frontend nav — badge count from polling or SSE, dropdown of recent notifications
- [ ] Add Resend email integration — send email for connection accepted, intro request received, and weekly digest
- [ ] Add browser push notification opt-in — use Web Push API; prompt user after first login

---

### Milestone 15: Multi-City Markdown Graph Expansion
**Goal:** At least 3 cities have complete, verified Markdown graph data — Chicago, Boston, and NYC.

Tasks:
- [x] Existing Cypher seed packs cover Chicago, Boston, and NYC
- [x] Add city selector to `ProfileForm.jsx` Step 1 — dropdown of supported cities with "More cities coming soon" for unsupported entries
- [ ] Convert Chicago seed data to Markdown graph nodes — Done when: Markdown validation passes and profile matching returns expected Chicago coverage
- [ ] Convert Boston seed data to Markdown graph nodes — Done when: Boston profile match returns ≥ 5 mentors and ≥ 10 local entities
- [ ] Convert NYC seed data to Markdown graph nodes — Done when: New York profile match returns ≥ 5 mentors and ≥ 10 local entities
- [ ] Add metadata quality checks for Markdown graph — Done when: `python -m app.db.validate_graph` reports on all 3 cities

---

### Milestone 16: Deploy
**Goal:** Platform is live at a public URL; Neon, Markdown graph data, AI providers, and optional email/storage services are connected in production.

Tasks:
- [ ] Build frontend with `npm run build` and deploy `frontend/dist` to Vercel — Done when: public Vercel URL loads the app
- [ ] Deploy FastAPI backend to Railway/Render/Fly with all env vars set via platform secrets — Done when: `GET /health`, `GET /health/graph`, and `GET /health/providers` return expected statuses
- [ ] Configure Neon production database, migrations, and Neon Auth keys — Done when: signup/login works on the production URL
- [ ] Set `VITE_API_BASE_URL` and Neon Auth client env vars in Vercel — Done when: frontend API calls authenticate successfully in production
- [ ] Configure custom domain (if available) on Vercel — Done when: app loads at the custom domain with HTTPS
- [ ] Smoke-test the full platform flow on production: signup → onboarding → plan → explore → chat → connection request → feed
- [ ] Add deploy config (`railway.toml`, Render blueprint, or Fly config) to repo root for reproducible backend deploys

---

### Milestone 17: Polish
**Goal:** No obvious errors; loading states present; edge cases handled; branding consistent.

Tasks:
- [x] Audit all UI copy for Globalदोस्त branding — zero product-facing "GlobalBuddy" strings in `frontend/src` — Done when: grep finds no product-facing instances
- [x] PlanPanel already has loading skeletons; FeedPage is persistence-backed work for a later milestone; ExploreWorkspace is prop-driven (no async loading state needed)
- [x] Add React error boundary in `App.jsx` — catches unhandled errors and shows "Something went wrong, please refresh" — Done when: throwing inside any panel renders the fallback
- [x] API error states: ProfileForm, PlanPanel, PreArrivalPage, ChatPage all surface errors via Banner or inline error div; graph-source errors surface through plan/profile API error paths
- [x] Add verification disclaimer to all entity cards (NodeDetailCard) and PlanPanel timeline — Done when: disclaimer text is visible on every card
- [ ] Accessibility deep audit — tab-key navigation through 3-step form and dashboard (ARIA labels added; full keyboard flow test pending manual verification)

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
claude "Read PLAN.md and complete Milestone 4 (Markdown Knowledge Graph Engine). Mark tasks done as you go. Stop after Milestone 4 and commit."
```

**Test current state:**
```
claude "Read PLAN.md. Without building anything new, test everything marked done. Run pytest for backend, check the platform flow in the browser. Report what works and what's broken."
```

---

## Notes & Decisions

- **Markdown graph + Neon split:** Markdown owns public/static knowledge (cities, universities, tasks, local places, seed mentors, guides, groups). Neon Postgres owns private/dynamic user data (profiles, progress, chat, connections, notifications). Never store private user data in Markdown.
- **Auth token flow:** Neon Auth issues a JWT on login. The frontend sends it as `Authorization: Bearer <token>` on protected API calls. FastAPI verifies against the configured Neon Auth JWKS.
- **Gemini vs Groq routing:** Use Gemini 2.5 Flash for plan generation and multi-turn chat (needs high token count). Use Groq for cultural bridge one-off lookups (needs low latency). The existing provider factory handles this — add a `prefer_speed` flag to the AI call.
- **Stage progression:** Stage is set by the backend based on `arrival_date`. Users can also manually advance their stage. Never let stage go backward automatically.
- **Mentor opt-in only:** Never auto-graduate a user to mentor. It must be an explicit opt-in action. Mentors can pause or deactivate their availability without losing their history.
- **LinkedIn OAuth scope:** Basic OIDC (`openid profile email`) works without app review. Education history endpoint requires LinkedIn review (1–4 weeks). Build pre-fill to work without education data and treat university pre-fill as a bonus.
- **Neo4j optionality:** Keep the existing Neo4j/Cypher implementation only as a legacy adapter or future upgrade path. The MVP should run without graph database credentials.
- **Branding:** Product-facing name is **Globalदोस्त**. Code identifiers use `globaldost` or `globalbuddy`. Only update UI copy strings, never rename code symbols.
- **Maps migration:** Replace all `maps.google.com` link-outs with Leaflet embedded maps using OpenStreetMap tiles. No API key required. Add `leaflet` and `react-leaflet` to `frontend/package.json`.
- **Email privacy:** Intro request emails are sent by the backend via Resend — the requester never sees the mentor's raw email address. The mentor's email is only in the backend environment.
