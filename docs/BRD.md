# Globalदोस्त Business Requirements Document (BRD)

## 1. Product vision
Globalदोस्त helps international students settle into a US city with a calm, practical, graph-grounded onboarding journey.

Motto: "You didn't come this far to figure it out alone."

## 2. Problem statement
International students often face first-month friction:
- unclear task order (what to do first)
- weak trust signals (who to ask)
- low local context (where to go for familiar support)

## 3. Target users
- Primary: international students new to a US city
- Secondary: returning US-based international students who still need local support discovery
- Internal: demo/review stakeholders evaluating product readiness

## 4. Business goals
- Reduce first-month uncertainty with sequence-aware guidance.
- Improve trust via graph-ranked mentors and peers.
- Improve belonging with local context (worship, groceries, housing, exploration, transit, events).
- Maintain a polished, demo-ready experience with transparent fallback behavior.

## 5. Value proposition
Globalदोस्त combines:
- Neo4j relationship intelligence for deterministic matching and explainable graph context.
- AI plan synthesis for warm, practical next steps linked to evidence nodes.

Output is not generic advice; it is contextual, ordered, and traceable to known entities.

## 6. Success metrics (current release)
- User completes Step 1 and receives session-backed recommendations end-to-end.
- Step 2 generates plan with `best_next_action`, ordered steps, and provider metadata.
- Cultural Bridge returns usable explanation and action list for a term.
- Step 3 supports category exploration and graph-node drill-down.
- Health panel clearly communicates API/Neo4j availability.

## 7. In scope
- Guided 3-step UI: Profile, AI Plan, Explore Graph.
- Returning-user shortcut: skip plan when `new_to_us=false`.
- Maps handoff and preview for local places/events.
- Multi-provider AI backend with deterministic fallback.

## 8. Out of scope
- Full account/authentication lifecycle.
- Persistent cross-device plan completion state.
- Live events calendar guarantees.
- Nationwide production-scale data completeness.

## 9. Risks and mitigations
- Sparse city data.
  - Mitigation: seeded city-local graph lists and resource fallback.
- AI provider instability/timeouts.
  - Mitigation: provider abstraction + deterministic fallback payloads.
- User over-trust of non-live data.
  - Mitigation: explicit verification guidance in UI copy and notes.

## 10. Branding
- Product-facing name: **Globalदोस्त**.
