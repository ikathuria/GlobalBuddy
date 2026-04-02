# GlobalBuddy

GlobalBuddy is a graph-powered support platform for international students. **Neo4j AuraDB** is the source of truth for students, mentors, peers, tasks, resources, restaurants, and events. An **AI provider layer** turns graph evidence into a structured first-30-days plan and cultural-term explanations. The default implementation uses **Google Gemini** via environment variables; the same interface can host **RocketRide** or other providers later without rewriting the app.

Motto: *You didn’t come this far to figure it out alone.*

## What this repo contains

- **Documentation** in `docs/` (BRD, SRS, architecture, API, agents, prompts, demo runbook).
- **Backend** — FastAPI, Neo4j access, `/v1` routers, provider-based AI (`backend/app/services/ai/`).
- **Frontend** — Vite + React command center: profile match, vis-network graph, plan generation, cultural bridge drawer.
- **Seed data** — `data/seed/*.cypher` (MERGE-only) including the Priya demo path (Chicago / Illinois Institute of Technology, HackWithChicago 3.0, Luma, IIT OIA).

## Architecture (vertical slice)

1. Student submits profile → `POST /v1/profile/match` queries Neo4j, ranks mentors, builds **evidence bundle** + **subgraph**, stores session.
2. `POST /v1/plan/generate` loads evidence from the session (or request body), calls the **Judge** path through `get_ai_provider(settings)` → **Gemini** when `GEMINI_API_KEY` is set (`AI_PROVIDER=gemini` or `auto`).
3. `POST /v1/bridge/explain` runs the **Cultural Bridge** path through the same provider abstraction with structured JSON output and deterministic fallback on failure.
4. `GET /v1/graph/subgraph?session_id=…` returns the stored subgraph for vis-network.

## Environment variables

Copy `backend/.env.example` → `backend/.env` and fill:

| Variable | Purpose |
|----------|---------|
| `NEO4J_URI` | Aura URI (`neo4j+s://…`) |
| `NEO4J_USER` | Neo4j user |
| `NEO4J_PASSWORD` | Neo4j password |
| `GEMINI_API_KEY` | Google AI Studio / Gemini API key (recommended for demos) |
| `GEMINI_MODEL` | Model id (default in app: `gemini-2.0-flash`) |
| `AI_PROVIDER` | `gemini`, `rocketride_http`, `anthropic_httpx`, or `auto` (prefers Gemini when key present) |
| `ROCKETRIDE_URI` | RocketRide base (e.g. `wss://cloud.rocketride.ai`) — optional |
| `ROCKETRIDE_APIKEY` | Bearer token for RocketRide HTTP |
| `ROCKETRIDE_HTTP_COMPLETION_URL` | Full URL for RocketRide HTTP JSON completion (optional swap-in) |
| `ANTHROPIC_API_KEY` | Optional alternative LLM path |
| `CORS_ORIGINS` | Comma-separated origins (include `http://localhost:5173`) |

**Gemini setup:** create an API key in [Google AI Studio](https://aistudio.google.com/), set `GEMINI_API_KEY` and `GEMINI_MODEL`, and use `AI_PROVIDER=gemini` (or `auto` with Gemini key present). Do not commit secrets.

**Validation:** at least one of Gemini, RocketRide HTTP pair, or Anthropic must be configured so the app can start.

## Setup — backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with Neo4j and Gemini (or another provider).

### Seed Neo4j (run after DB is empty or idempotent re-run)

Seeding only needs **`NEO4J_URI`**, **`NEO4J_USER`**, **`NEO4J_PASSWORD`**. You do not need an LLM key to seed.

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_data
```

### Run API

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Setup — frontend

```bash
cd frontend
npm install
echo 'VITE_API_BASE_URL=http://127.0.0.1:8000' > .env.local
npm run dev
```

Open the printed URL (default [http://localhost:5173](http://localhost:5173)).

Optional: `VITE_API_TIMEOUT_MS` for long plan/bridge calls (default 180000).

## Tests (backend)

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

Covers health, profile match response shape, plan/bridge response shapes, and agent mocks.

## Demo flow (hackathon)

1. Seed Neo4j once per environment (`python -m app.db.seed_data`).
2. Configure `GEMINI_API_KEY` (and Neo4j) in `backend/.env`; start backend and frontend.
3. Confirm **API live** and Neo4j node count in the status panel (use **Retry check** if needed).
4. Submit the profile form (defaults: **Illinois Institute of Technology**, **Chicago**) → review **support / belonging scores**, mentor cards with **confidence** and **Why this match?**
5. Explore the **evidence graph** (hover tooltips, click nodes for detail); student/mentor/event/restaurant/resource colors are distinct.
6. Click **Generate my first 30 days** — structured plan with **best next action** at the top (evidence-grounded JSON).
7. Use **Explain term** or quick chips → **Cultural bridge** drawer (plain explanation, analogy, mistakes, next steps). Press **Escape** to close.

## Documentation index

- [BRD](./docs/BRD.md)
- [SRS](./docs/SRS.md)
- [Architecture](./docs/architecture.md)
- [Data model](./docs/data-model.md)
- [API spec](./docs/api-spec.md)
- [Agents spec](./docs/agents-spec.md)
- [Prompt spec](./docs/prompt-spec.md)
- [Demo runbook](./docs/demo-runbook.md)

## Team workflow

Use short-lived feature branches from `main`, own directories (`app/routers`, `app/db`, `frontend/src/components`), and open PRs early.

## Next phase (after this slice)

- Persist sessions (Redis/Postgres) instead of in-memory `SessionStore`.
- Streaming responses (SSE/WebSocket) per architecture doc.
- Expand graph coverage (more cities, richer ranking, events API).
- Implement `RocketRide` provider class behind the same `AIProvider` interface when your HTTP contract is fixed.
