# GlobalBuddy Architecture

## 1. System Overview
GlobalBuddy uses a backend-orchestrated multi-agent pipeline.

```mermaid
flowchart LR
  U[Student UI] --> B[FastAPI Orchestrator]
  B --> N[(Neo4j AuraDB)]
  B --> R[RocketRide AI]
  B --> V[WebSocket or SSE Stream]
  V --> U
```

## 2. Agent Orchestration
```mermaid
flowchart TD
  A[Input Profile] --> P[Profile and Match Agent]
  P --> G[Graph Evidence Bundle]
  G --> J[Judge Agent]
  G --> C[Cultural Bridge Agent]
  J --> O[Ordered 30-Day Plan]
  C --> X[Contextual Explanations]
  O --> UI[Command Center]
  X --> UI
```

## 3. Runtime Data Flow
1. Frontend posts profile.
2. Backend executes Neo4j queries for mentors, peers, restaurants, events, resources.
3. Backend computes ranking and confidence metadata.
4. Backend passes evidence bundle to RocketRide Judge Agent.
5. Judge returns ordered plan with citations to graph entities.
6. Frontend renders graph and cards incrementally via stream.

## 4. Subsystems
- Frontend (React + vis.js)
  - Profile form
  - Live graph visualization
  - Match cards
  - Timeline plan view
  - Cultural bridge drawer
- Backend (FastAPI)
  - Request validation
  - Agent orchestration
  - Neo4j query service
  - RocketRide prompt service
- Data (Neo4j AuraDB)
  - Relationship-first data model
  - Task dependency graph
- AI (RocketRide)
  - Judge narrative synthesis
  - Cultural term translation and analogies

## 5. Non-Functional Architecture Notes
- Use timeouts and retries around AI calls.
- Log evidence IDs used in generated plan for auditability.
- Keep ranking deterministic before narrative generation.
