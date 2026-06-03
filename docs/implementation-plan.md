# Globalदोस्त Implementation Plan

## 1. Current Baseline
The current implementation already includes:
- Guided 3-step frontend journey
- Session-backed profile match + evidence bundle
- Plan generation and cultural explanation endpoints
- Explore workspace with graph drill-down and category views
- Multi-provider AI abstraction with deterministic fallbacks
- Legacy Neo4j seed data and graph adapter code

## 2. Strategic Direction
Move the MVP data architecture to:

```text
Markdown knowledge graph
  public/static city knowledge

Neon Auth + Neon Postgres
  private/dynamic user and product data
```

Neo4j remains optional as a future graph-database adapter if the relationship layer becomes too dynamic for Markdown.

## 3. Near-Term Phases

### Phase A: Markdown Graph Engine
1. Define Markdown frontmatter schema and folder conventions.
2. Convert a small Chicago slice from Cypher seed data to Markdown.
3. Parse YAML frontmatter, `links_to`, `depends_on`, and `[[wikilinks]]`.
4. Build an in-memory graph index and validation report.
5. Add `MarkdownGraphService` behind a graph adapter interface.
6. Update `/v1/profile/match`, `/v1/graph/subgraph`, and target `/health/graph`.
7. Add tests for parsing, validation, ranking, and task dependency ordering.

### Phase B: Neon Auth and Persistence
1. Add Postgres migration tooling and repository layer.
2. Configure Neon project and Neon Auth / Stack Auth keys.
3. Integrate `/auth` with Neon Auth.
4. Verify JWTs in FastAPI through Stack Auth JWKS.
5. Create app tables for profiles, plan progress, documents, chat, connections, content, mentors, and notifications.
6. Migrate plan completion and document tracker state out of localStorage.

### Phase C: Product Expansion
1. Convert Boston and NYC graph data to Markdown.
2. Add feed and saved content from Markdown + Neon.
3. Add connection requests and mentor introductions.
4. Add mentor opt-in and rating flows.
5. Add notifications through polling first, then SSE/WebSocket if needed.

## 4. Reliability Goals
1. Keep structured logs around provider selection, latency, graph source, and fallback status.
2. Improve timeout/error telemetry for `plan`, `bridge`, and `chat` routes.
3. Keep regression tests for `new_to_us=false` skip behavior.
4. Validate Markdown graph data in CI.
5. Keep public onboarding functional even when Neon persistence is unavailable.

## 5. UX Evolution Roadmap
1. Persist plan progress server-side.
2. Add richer "why recommended" explanations for each category card.
3. Add export/share option for first-30-days plan.
4. Add confidence bands per recommendation cluster.
5. Move Cultural Bridge one-off lookups into persistent chat.

## 6. Quality Gates
- Unit tests for agents, routers, and graph parsing pass.
- Health endpoints report expected state.
- Profile -> plan -> explore flow works with and without AI fallback.
- Markdown graph validation has zero errors for supported cities.
- Docs remain updated with every UI/API/data contract change.

## 7. Ownership Suggestions
- Data/graph: Markdown schema, seed conversion, ranking policy, validation.
- Backend/API: graph adapter, Neon repositories, provider layer, fallback logic.
- Frontend: step flow, auth screens, graph interactions, accessibility.
- QA/demo: scripted walkthroughs, smoke checks, graph validation fixtures.

## 8. Definition of Done for Next Milestone
- App can complete the 3-step journey without Neo4j credentials.
- Markdown graph drives profile matching, plan evidence, and subgraph visualization.
- `/health/graph` reports node/edge counts and validation status.
- Existing tests pass or are updated to mock the graph adapter rather than Neo4j.
