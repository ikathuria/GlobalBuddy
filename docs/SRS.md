# Globalदोस्त Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose
Define functional and non-functional requirements for the current Globalदोस्त web application.

### 1.2 Scope
Globalदोस्त captures arrival context, builds Neo4j-backed recommendations, generates a first-30-days plan, explains unfamiliar terms, and supports graph-first exploration.

### 1.3 Intended audience
- Engineers
- Product and design collaborators
- Demo and QA stakeholders

## 2. Product overview
- React frontend with guided 3-step journey
- FastAPI backend
- Neo4j AuraDB data source
- AI provider abstraction (Gemini, RocketRide SDK/HTTP, Anthropic) with deterministic fallback

## 3. Functional requirements
- FR-1 Profile wizard
  - System shall collect required fields across 3 profile steps.
- FR-2 Session-backed matching
  - System shall create `session_id` and return graph-backed recommendations.
- FR-3 Mentor/peer recommendations
  - System shall return ranked mentors and peers with explanation fields.
- FR-4 Local intelligence
  - System shall return worship/grocery/housing/exploration/transit lists when available.
- FR-5 Plan generation
  - System shall generate ordered plan steps through provider abstraction.
- FR-6 Returning-user branch
  - UI shall skip plan step when profile indicates user has lived in US before.
- FR-7 Cultural Bridge
  - System shall explain term with analogy, mistakes, and next actions.
- FR-8 Graph exploration
  - UI shall render subgraph, support node selection, filter groups, and path highlighting.
- FR-9 Map handoff
  - UI shall expose Google Maps open links and optional embed preview when query exists.
- FR-10 Health visibility
  - UI shall display API and Neo4j health indicators with retry behavior.

## 4. Non-functional requirements
- NFR-1 Usability
  - First-time user should understand progression without training.
- NFR-2 Reliability
  - Failure in AI provider must still produce deterministic structured output.
- NFR-3 Performance
  - Match responses should feel interactive for demo-scale data.
- NFR-4 Explainability
  - Plan steps should preserve evidence-linked entities.
- NFR-5 Accessibility
  - Keyboard support for key overlays/drawers and readable visual contrast.
- NFR-6 Maintainability
  - UI, agents, data access, and provider logic should remain modular.

## 5. Data requirements
- Neo4j labels include people, resources, tasks, events, and local place/transit entities.
- Task ordering depends on `Task-[:PRECEDES]->Task`.
- Session data must preserve evidence bundle and subgraph for subsequent API calls.

## 6. External interfaces
- REST endpoints under `/v1` for profile, plan, bridge, and graph.
- Health endpoints at `/health` and `/health/neo4j`.
- Neo4j via official driver.
- Provider calls through backend abstraction layer.

## 7. Acceptance criteria
- AC-1 Profile submission returns `session_id`, recommendations, scores, and subgraph.
- AC-2 Plan generation returns structured timeline with provider metadata.
- AC-3 Bridge explanation returns all schema fields.
- AC-4 Explore graph supports selecting a node and viewing details.
- AC-5 Returning-user flow opens Step 3 directly after profile submit.
- AC-6 Health panel accurately reflects backend and Neo4j state.
