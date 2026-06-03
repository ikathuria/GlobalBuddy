# Globalदोस्त Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose
Define functional and non-functional requirements for the Globalदोस्त web application and its target MVP architecture.

### 1.2 Scope
Globalदोस्त captures arrival context, builds Markdown-graph-backed recommendations, generates a first-30-days plan, explains unfamiliar terms, and supports graph-first exploration. Auth and persistent user data are handled by Neon Auth and Neon Postgres in the target roadmap.

### 1.3 Intended Audience
- Engineers
- Product and design collaborators
- Demo and QA stakeholders

## 2. Product Overview
- React frontend with guided 3-step journey
- FastAPI backend
- Markdown knowledge graph for public/static city knowledge
- Neon Auth + Neon Postgres for accounts and private/dynamic user data
- AI provider abstraction (Gemini, Groq, Anthropic, legacy RocketRide paths) with deterministic fallback

## 3. Functional Requirements
- FR-1 Profile wizard
  - System shall collect required fields across 3 profile steps.
- FR-2 Session-backed matching
  - System shall create `session_id` and return graph-backed recommendations.
- FR-3 Mentor/peer recommendations
  - System shall return ranked mentors and peers with explanation fields.
- FR-4 Local intelligence
  - System shall return worship/grocery/housing/exploration/transit/group lists when available.
- FR-5 Plan generation
  - System shall generate ordered plan steps through provider abstraction.
- FR-6 Returning-user branch
  - UI shall skip plan step when profile indicates user has lived in the US before.
- FR-7 Cultural Bridge
  - System shall explain terms with analogy, mistakes, and next actions.
- FR-8 Graph exploration
  - UI shall render subgraph, support node selection, filter groups, and path highlighting.
- FR-9 Map handoff and preview
  - UI shall expose map links and, later, Leaflet/OpenStreetMap embeds when location metadata exists.
- FR-10 Health visibility
  - UI shall display API, provider, and graph-source health indicators with retry behavior.
- FR-11 Persistent accounts
  - System shall persist profiles, plan progress, documents, chat, connections, and notifications in Neon Postgres once auth is enabled.

## 4. Non-Functional Requirements
- NFR-1 Usability
  - First-time user should understand progression without training.
- NFR-2 Reliability
  - Failure in AI provider must still produce deterministic structured output.
- NFR-3 Performance
  - Match responses should feel interactive for demo-scale Markdown graph data.
- NFR-4 Explainability
  - Plan steps should preserve evidence-linked entities and source node ids.
- NFR-5 Accessibility
  - Keyboard support for key overlays/drawers and readable visual contrast.
- NFR-6 Maintainability
  - UI, agents, graph adapters, data access, and provider logic should remain modular.
- NFR-7 Privacy
  - Private user data must be stored only in Neon Postgres, never in Markdown graph files.

## 5. Data Requirements
- Markdown graph nodes include people, resources, tasks, guides, events, groups, and local place/transit entities.
- Task ordering depends on `depends_on` frontmatter edges.
- `[[wikilinks]]` and explicit frontmatter links generate graph edges.
- Session data must preserve evidence bundle and subgraph for subsequent API calls.
- Neon Postgres stores private/dynamic app data.

## 6. External Interfaces
- REST endpoints under `/v1` for profile, plan, bridge, graph, chat, auth, and future social/feed features.
- Health endpoints at `/health`, `/health/providers`, and target `/health/graph`.
- Neon Postgres via backend repository layer.
- Neon Auth JWT verification through JWKS.
- Provider calls through backend abstraction layer.
- Legacy Neo4j adapter may remain available during migration but is not required for the target MVP.

## 7. Acceptance Criteria
- AC-1 Profile submission returns `session_id`, recommendations, scores, and subgraph.
- AC-2 Plan generation returns structured timeline with provider metadata.
- AC-3 Bridge explanation returns all schema fields.
- AC-4 Explore graph supports selecting a node and viewing details.
- AC-5 Returning-user flow opens Step 3 directly after profile submit.
- AC-6 Health panel accurately reflects backend, provider, and graph-source state.
- AC-7 Markdown graph validation catches duplicate ids, broken links, missing required fields, and task dependency cycles.
- AC-8 Authenticated plan progress persists across devices after Neon integration.
