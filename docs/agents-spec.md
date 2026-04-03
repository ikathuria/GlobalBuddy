# Globalदोस्त Agent Specifications

## 1. Shared agent contract
Each agent receives:
- `session_id` (when applicable)
- `student_profile`
- `evidence_bundle`
- provider settings resolved from backend config

Each agent returns:
- structured JSON payload (schema-defined)
- `confidence`
- `fallback_used`
- `llm_provider`

## 2. Profile and Match agent

### Responsibility
Build deterministic graph-backed recommendations from Neo4j and return a session-scoped evidence bundle.

### Inputs
- `ProfileMatchRequest`
- Neo4j graph state

### Outputs
- `mentors_top3`, `peers_nearby`, `cultural_restaurants`, `community_events`, `resources`
- local intelligence lists: `places_of_worship`, `grocery_stores`, `housing_areas`, `exploration_spots`, `transit_tips`
- ranking scores: `support_coverage_score`, `belonging_score`, `cultural_fit_score`
- `best_weekend_outing`
- `subgraph` (nodes + edges)

### Deterministic ranking policy
Mentor score weights:
- shared country: `0.30`
- shared university: `0.25`
- need overlap: `0.25`
- trust score: `0.20`

## 3. Judge agent (plan generation)

### Responsibility
Generate an ordered first-30-days plan from graph evidence through the selected AI provider.

### Provider behavior
- Provider selected by `AI_PROVIDER` (`auto` prefers Gemini when key exists).
- On provider failure, return deterministic checklist fallback from task graph.

### Hard requirements
- Use evidence entities only (citation validation runs server-side).
- Preserve dependency order from `tasks_ordered`.
- Return JSON shape expected by `PlanGenerateResponse`.

### Output schema highlights
- `plan_title`
- `best_next_action`
- `steps[]` with `day_range`, `action`, `entities`, `dependency_reason`, `source_node_ids`
- `priority_contacts`, `warnings`, `confidence`, `fallback_used`, `llm_provider`

## 4. Cultural Bridge agent

### Responsibility
Explain unfamiliar local terms in plain language using home-country context.

### Trigger points
- User presses "Explain term" in Step 2
- User taps quick chips (`security deposit`, `credit score`, `SSN`)

### Output schema highlights
- `term`
- `plain_explanation`
- `home_context_analogy`
- `common_mistakes[]`
- `what_to_do_next[]`
- `fallback_used`, `llm_provider`

## 5. Fallback rules
- If AI generation fails, return deterministic structured output (never free-form empty text).
- If graph entities are sparse, return best available recommendations with warnings.
- For events/maps/transit details, keep disclaimer language that dates/routes must be independently verified.
