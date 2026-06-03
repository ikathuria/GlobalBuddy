# Globalदोस्त Business Requirements Document (BRD)

## 1. Product Vision
Globalदोस्त helps international students settle into a US city with a calm, practical, graph-grounded onboarding journey.

Motto: "You didn't come this far to figure it out alone."

## 2. Problem Statement
International students often face first-month friction:
- unclear task order: what to do first
- weak trust signals: who to ask
- low local context: where to go for familiar support

## 3. Target Users
- Primary: international students new to a US city
- Secondary: returning US-based international students who still need local support discovery
- Internal: demo/review stakeholders evaluating product readiness

## 4. Business Goals
- Reduce first-month uncertainty with sequence-aware guidance.
- Improve trust via graph-ranked mentors and peers.
- Improve belonging with local context: worship, groceries, housing, exploration, transit, events, and groups.
- Keep the MVP cheap to run across multiple active projects by using Neon and Git-backed Markdown data.
- Maintain a polished, demo-ready experience with transparent fallback behavior.

## 5. Value Proposition
Globalदोस्त combines:
- An editable Markdown knowledge graph for deterministic matching and explainable local context.
- Neon Auth/Postgres for persistent, private user journeys.
- AI plan synthesis for warm, practical next steps linked to evidence nodes.

Output is not generic advice; it is contextual, ordered, and traceable to known entities.

## 6. Success Metrics
- User completes Step 1 and receives session-backed recommendations end-to-end.
- Step 2 generates a plan with `best_next_action`, ordered steps, and provider metadata.
- Cultural Bridge returns usable explanation and action list for a term.
- Step 3 supports category exploration and graph-node drill-down.
- Health panel clearly communicates API, provider, and graph-source availability.
- After Neon integration, plan progress persists across sessions/devices.

## 7. In Scope
- Guided 3-step UI: Profile, AI Plan, Explore Graph.
- Returning-user shortcut: skip plan when `new_to_us=false`.
- Markdown knowledge graph for public/static city data.
- Neon Auth/Postgres for accounts and private/dynamic app data.
- Maps handoff and preview for local places/events.
- Multi-provider AI backend with deterministic fallback.

## 8. Out of Scope
- Nationwide production-scale data completeness.
- Live events calendar guarantees.
- File uploads until a real product workflow requires R2.
- Realtime collaboration; use polling/SSE/WebSocket only when needed.
- Neo4j as a required production dependency for the MVP.

## 9. Risks and Mitigations
- Sparse city data.
  - Mitigation: Markdown validation, required city coverage checks, and reusable seed templates.
- AI provider instability/timeouts.
  - Mitigation: provider abstraction + deterministic fallback payloads.
- User over-trust of non-live data.
  - Mitigation: explicit verification guidance in UI copy and notes.
- Markdown graph gets too dynamic for Git.
  - Mitigation: keep graph adapter boundary so Neo4j/Memgraph can be reintroduced later.

## 10. Branding
- Product-facing name: **Globalदोस्त**.
