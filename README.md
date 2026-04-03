# Globalदोस्त

Globalदोस्त is a graph-powered support platform for international students arriving in US cities. The current product experience is a guided 3-step journey that turns profile context plus Neo4j evidence into practical next actions.

Motto: *You didn't come this far to figure it out alone.*

## What is live now

- **Step 1 - Profile setup wizard**
  - 3 sections: Personal Info, Origin and Context, Destination.
  - Smart starter defaults for a faster demo path.
  - Supports optional cultural context fields (`cultural_background`, `religion_or_observance`, `diet`) and social handles.
  - `new_to_us=false` is used to skip the plan step in the UI.

- **Step 2 - AI Plan (first 30 days)**
  - Calls `POST /v1/plan/generate` with session-backed evidence.
  - Week-grouped timeline, best next action, warning surface, and provider/fallback metadata.
  - Task completion is persisted per session in browser local storage.
  - Each plan step can focus related graph nodes.

- **Step 3 - Explore Graph**
  - Category views: People, Events, Food, Housing, Tasks.
  - Person profile modal with one-click contact links (email/LinkedIn/Instagram/phone when available).
  - vis-network graph with filter chips, path highlighting, shortest-path breadcrumb, and fit/expand controls.
  - Node detail panel supports direct Maps open plus embedded map preview.

- **Cultural Bridge drawer**
  - Calls `POST /v1/bridge/explain` from custom term input or quick chips (`security deposit`, `credit score`, `SSN`).
  - Returns plain explanation, home-context analogy, common mistakes, and next actions.

- **System status checks**
  - UI probes `GET /health` and `GET /health/neo4j`.
  - Shows API live/offline state and Neo4j node count with retry.

## Backend stack

- FastAPI (`backend/app`)
- Neo4j AuraDB as source of truth for graph evidence
- AI provider abstraction:
  - `gemini` (default-recommended)
  - `rocketride_sdk`
  - `rocketride_http` (legacy compatibility)
  - `anthropic`
  - deterministic fallback when generation fails

## API surface

- `POST /v1/profile/match`
- `POST /v1/plan/generate`
- `POST /v1/bridge/explain`
- `GET /v1/graph/subgraph?session_id=...`
- `GET /health`
- `GET /health/neo4j`

## Environment variables

Copy `backend/.env.example` to `backend/.env`.

| Variable | Purpose |
|---|---|
| `NEO4J_URI` | Aura URI (`neo4j+s://...`) |
| `NEO4J_USER` | Neo4j user |
| `NEO4J_PASSWORD` | Neo4j password |
| `AI_PROVIDER` | `auto`, `gemini`, `rocketride_sdk`, `rocketride_http`, `anthropic` |
| `GEMINI_API_KEY` | Gemini key (recommended path) |
| `GEMINI_MODEL` | Gemini model id (default `gemini-2.0-flash`) |
| `ROCKETRIDE_URI` | RocketRide base URI |
| `ROCKETRIDE_APIKEY` | RocketRide API key |
| `ROCKETRIDE_GEMINI_KEY` | Gemini key passed to RocketRide pipelines |
| `ROCKETRIDE_PLAN_PIPELINE` | Plan pipeline path |
| `ROCKETRIDE_BRIDGE_PIPELINE` | Bridge pipeline path |
| `ROCKETRIDE_HTTP_COMPLETION_URL` | Legacy RocketRide HTTP completion URL |
| `ANTHROPIC_API_KEY` | Anthropic key |
| `CORS_ORIGINS` | Comma-separated allowed origins |

Validation rule: at least one provider path must be configured (`GEMINI_API_KEY`, RocketRide SDK pair, RocketRide HTTP pair, or `ANTHROPIC_API_KEY`).

## Local setup

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run API:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Seed graph data

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_data
```

The seed script only needs Neo4j variables.

### 3) Frontend

```bash
cd frontend
npm install
echo 'VITE_API_BASE_URL=http://127.0.0.1:8000' > .env.local
npm run dev
```

Optional: set `VITE_API_TIMEOUT_MS` (default `180000`).

## Demo flow

1. Open app and verify status pills show API and Neo4j health.
2. Complete Step 1 profile wizard and submit.
3. If `new_to_us=true`, generate plan in Step 2; if false, Step 2 is skipped and Step 3 opens directly.
4. Use "Explain term" to open Cultural Bridge.
5. In Step 3, switch categories, focus cards into graph, and inspect node details with Maps.

## Documentation index

- [BRD](./docs/BRD.md)
- [SRS](./docs/SRS.md)
- [Architecture](./docs/architecture.md)
- [Data model](./docs/data-model.md)
- [API spec](./docs/api-spec.md)
- [Agents spec](./docs/agents-spec.md)
- [Prompt spec](./docs/prompt-spec.md)
- [Demo runbook](./docs/demo-runbook.md)
- [Implementation plan](./docs/implementation-plan.md)
