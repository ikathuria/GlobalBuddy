# GlobalBuddy Detailed Implementation Plan

## 1. Delivery Goal
Build a hackathon-ready, end-to-end GlobalBuddy MVP that:
- Uses Neo4j AuraDB as the primary source of connected truth.
- Uses RocketRide AI for core intelligent behavior (plan generation + cultural bridge).
- Demonstrates a polished hero journey in a live demo.

Default hero scenario:
- Origin: India
- Destination: UT Austin (Austin, TX)
- Needs: banking + housing
- Interests: South Indian food + community events

## 2. Team Execution Model
Recommended parallel workstreams:
- Track A: Data + Neo4j (schema, seed, query tuning)
- Track B: Backend + Agents (FastAPI, orchestration, tooling)
- Track C: Frontend + UX (React, vis.js command center)
- Track D: QA + Demo (test scripts, reliability, pitch flow)

Definition of done (project):
- User can submit profile and get graph-backed mentor/peer/cultural/event results.
- Judge Agent generates ordered 30-day plan with named entities and dependency-aware order.
- Cultural Bridge explanation works on selected terms.
- Live graph visualization updates with match highlights.
- Demo run is repeatable and stable.

## 3. Step-by-Step Implementation

### Phase 0: Environment and Repo Bootstrap
1. Confirm local prerequisites:
   - Node.js LTS, Python 3.11+ (or team standard), git.
   - Neo4j AuraDB credentials.
   - RocketRide API key and endpoint details.
2. Create project structure:
   - `backend/`, `frontend/`, `scripts/`, `docs/`.
3. Set up environment variable templates:
   - `backend/.env.example` with Neo4j and RocketRide variables.
   - `frontend/.env.example` with API base URL.
4. Create startup scripts:
   - `scripts/dev-backend.*`, `scripts/dev-frontend.*`.
5. Exit criteria:
   - Team can run backend and frontend locally with placeholder health checks.

### Phase 1: Neo4j Schema and Seed Data
1. Implement graph schema from `docs/data-model.md`.
2. Add constraints and indexes first.
3. Define seed dataset format (CSV or JSON):
   - Countries, universities, needs, tasks, mentors, peers, resources, restaurants, events.
4. Build deterministic seed scripts under `scripts/`:
   - `seed_base`, `seed_hero_scenario`, `seed_events`.
5. Model dependency logic using `(:Task)-[:PRECEDES]->(:Task)`.
6. Add smoke query scripts:
   - Top mentors for hero student.
   - Upcoming events by culture + city.
   - Task ordering query for needs.
7. Exit criteria:
   - Seed completes without errors.
   - Hero student query returns at least:
     - 3 mentors
     - 3 peers
     - 3 restaurants
     - 3 events/resources

### Phase 2: Backend Foundation (FastAPI)
1. Initialize FastAPI service in `backend/`.
2. Add config loader:
   - Neo4j URI/user/pass, RocketRide key, timeout values.
3. Build service layers:
   - `graph_service` for Cypher execution.
   - `ranking_service` for deterministic scoring.
   - `ai_service` for RocketRide calls.
4. Implement base endpoints and contracts:
   - `POST /v1/profile/match`
   - `POST /v1/plan/generate`
   - `POST /v1/bridge/explain`
   - `GET /v1/graph/subgraph`
   - `GET /v1/events/upcoming`
5. Add unified error envelope and trace IDs.
6. Add request/response schema validation (Pydantic models).
7. Exit criteria:
   - API responses match `docs/api-spec.md`.
   - Health checks and error handling are working.

### Phase 3: Agentic Orchestration
1. Implement Profile and Match Agent:
   - Parse student profile.
   - Execute Neo4j retrieval queries.
   - Rank results with weighted scoring.
   - Return evidence bundle + subgraph.
2. Implement Judge Agent:
   - Retrieve dependency chain for requested needs.
   - Build RocketRide prompt from structured evidence only.
   - Generate ordered plan with citation fields.
3. Implement Cultural Bridge Agent:
   - Term + country + context input.
   - RocketRide explanation output with analogy + mistakes + next actions.
4. Add fallback behavior:
   - Sparse match fallback text.
   - AI timeout fallback to deterministic checklist from task graph.
5. Add orchestration endpoint flow:
   - `profile/match` -> evidence
   - `plan/generate` -> narrative plan
   - optional bridge calls from UI interactions
6. Exit criteria:
   - Agents produce valid JSON contracts.
   - Plan order respects dependency chain consistently.

### Phase 4: Frontend Command Center (React + vis.js)
1. Build page layout:
   - Profile form panel
   - Live graph panel
   - Recommendation cards panel
   - Survival plan timeline panel
   - Cultural bridge drawer
2. Implement profile form with validation.
3. Wire match API call and render:
   - Top mentors card section.
   - Nearby peers section.
   - Cultural comfort section (food + events).
4. Implement vis.js graph rendering:
   - Student as center node.
   - Dynamic node/edge insertion as matches return.
   - Highlight animation for newly matched entities.
5. Implement plan generation UI:
   - Trigger `/plan/generate`.
   - Render day-range ordered steps with entity chips.
6. Implement cultural explain action:
   - Click term -> call `/bridge/explain`.
   - Show response in side drawer/modal.
7. Add loading/error/empty states for all panes.
8. Exit criteria:
   - One-click hero flow works without manual data edits.
   - UI remains usable on laptop and mobile widths.

### Phase 5: Quality and Reliability
1. Backend tests:
   - Schema validation tests.
   - Ranking correctness tests.
   - Dependency ordering tests.
   - Error envelope tests.
2. Query tests:
   - Cypher correctness with seeded dataset.
   - Performance checks on key match queries.
3. Frontend tests:
   - Form validation.
   - Card rendering from API payload.
   - Timeline ordering assertions.
4. End-to-end test script:
   - Hero scenario input -> expected artifacts present.
5. Add observability basics:
   - request timing logs
   - RocketRide latency logs
   - failed query tracking
6. Exit criteria:
   - Hero path passes end-to-end test repeatedly.
   - Core response times meet SRS targets in demo environment.

### Phase 6: Demo Hardening and Story
1. Freeze seed data and demo account values.
2. Add demo mode config (stable deterministic responses where needed).
3. Build a live run script checklist:
   - start order
   - env verification
   - backup fallback mode
4. Prepare demo narrative aligned to judging criteria:
   - graph intelligence
   - AI intelligence
   - user impact
5. Practice 3-minute and 5-minute variants from `docs/demo-runbook.md`.
6. Exit criteria:
   - Team can recover from one subsystem failure and continue demo.

## 4. Detailed Milestone Checklist

### Milestone M1: Data Ready
- Schema applied in AuraDB.
- Seed scripts committed.
- Hero scenario returns complete recommendation set.

### Milestone M2: API Ready
- All v1 endpoints implemented and documented.
- Error handling and tracing added.
- Postman/HTTP collection validated.

### Milestone M3: Agent Ready
- Profile and Match Agent returns ranked evidence bundle.
- Judge Agent returns ordered, entity-cited plan.
- Cultural Bridge Agent returns contextual explanation.

### Milestone M4: UX Ready
- Command center connected to live APIs.
- Graph highlight flow functioning.
- Plan timeline and bridge drawer polished.

### Milestone M5: Demo Ready
- End-to-end hero script reliable.
- Backup path tested.
- Pitch synced with product output.

## 5. Acceptance Test Scenarios
1. Hero scenario (India, UT Austin, banking + housing):
   - Returns top 3 mentors with match reasons.
   - Returns peers/restaurants/events.
   - Generates ordered plan with named entities.
2. Sparse data scenario:
   - Missing mentors still returns alternatives + confidence note.
3. Cultural term scenario:
   - \"security deposit\" explanation includes home-country analogy and immediate actions.
4. Ordering scenario:
   - Plan steps do not violate dependency graph order.
5. Resilience scenario:
   - AI timeout triggers deterministic fallback checklist.

## 6. Risk Register and Mitigation
- Risk: Data sparsity in target city.
  - Mitigation: Curated seed pack and fallback resource nodes.
- Risk: AI generic output.
  - Mitigation: Evidence-only prompts and output schema validation.
- Risk: Demo instability.
  - Mitigation: Cached hero dataset + startup checklist + fallback mode.
- Risk: Team bandwidth.
  - Mitigation: Parallel tracks with milestone handoff dates.

## 7. Suggested Execution Timeline (Hackathon)
Day 1:
- Phase 0 + Phase 1 complete.
- Start Phase 2 backend scaffolding.

Day 2:
- Finish Phase 2 and Phase 3 agent flow.
- Begin Phase 4 frontend integration.

Day 3:
- Finish Phase 4.
- Execute Phase 5 tests and bug fixes.
- Start Phase 6 demo hardening.

Final half-day:
- Demo rehearsal loops.
- Freeze branch and prep final pitch assets.

## 8. Immediate Next Actions
1. Scaffold backend and frontend folders with starter apps.
2. Implement Neo4j schema and seed scripts first.
3. Build `POST /v1/profile/match` as the first working vertical slice.
4. Add Judge Agent plan generation once evidence bundle is stable.
5. Finish UI wiring and run hero demo rehearsal.
