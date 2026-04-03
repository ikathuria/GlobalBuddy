# Globalदोस्त Implementation Plan

## 1. Current baseline
The current implementation already includes:
- Guided 3-step frontend journey
- Session-backed profile match + evidence bundle
- Plan generation and cultural explanation endpoints
- Explore workspace with graph drill-down and category views
- Multi-provider AI abstraction with deterministic fallbacks

## 2. Stabilization goals (near-term)

### Phase A: Documentation and product alignment
1. Keep README and specs aligned with live UI copy/flows.
2. Maintain naming consistency for Globalदोस्त while preserving code compatibility.
3. Keep API examples synchronized with actual schema fields.

### Phase B: Reliability hardening
1. Add structured logs around provider selection and latency.
2. Improve timeout/error telemetry for `plan` and `bridge` routes.
3. Add regression tests for `new_to_us=false` skip behavior in UI and API contract compatibility.

### Phase C: Data quality and local intelligence
1. Expand city seed packs beyond the current hero path.
2. Add stronger metadata quality checks for maps/event/resource nodes.
3. Keep verification disclaimers for any non-live data.

## 3. UX evolution roadmap
1. Persist plan progress server-side (optional account/session persistence).
2. Add richer "why recommended" explanations for each category card.
3. Add export/share option for first-30-days plan.
4. Add confidence bands per recommendation cluster.

## 4. Backend roadmap
1. Move in-memory session store to Redis/Postgres.
2. Add provider health diagnostics endpoint.
3. Introduce optional streaming for long-running plan generation.
4. Add stricter schema validation for AI output before response serialization.

## 5. Quality gates
- Unit tests for agents and routers pass.
- Health endpoints report expected state.
- Profile -> plan -> explore flow works with and without AI fallback.
- Docs remain updated with every UI contract change.

## 6. Ownership suggestions
- Data/graph: schema, seed packs, ranking policy
- Backend/API: contracts, provider layer, fallback logic
- Frontend: step flow, graph interactions, accessibility
- QA/demo: scripted walkthroughs and smoke checks

## 7. Definition of done (next milestone)
- Users can complete all 3 steps with clear state transitions.
- Docs accurately describe current behavior and payloads.
- Failure modes are understandable and recoverable in UI.
- Globalदोस्त branding is consistent across product-facing docs.
