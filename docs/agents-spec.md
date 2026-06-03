# Globalदोस्त Agent Specifications

## 1. Shared Agent Contract
Each agent receives:
- `session_id` when applicable
- `student_profile`
- `evidence_bundle`
- provider settings resolved from backend config

Each agent returns:
- structured JSON payload matching API schemas
- `confidence`
- `fallback_used`
- `llm_provider`

## 2. Profile and Match Agent

### Responsibility
Build deterministic graph-backed recommendations from the Markdown graph index and return a session-scoped evidence bundle.

### Inputs
- `ProfileMatchRequest`
- Markdown graph index
- Optional logged-in user profile from Neon Postgres

### Outputs
- `mentors_top3`, `peers_nearby`, `cultural_restaurants`, `community_events`, `resources`
- local intelligence lists: `places_of_worship`, `grocery_stores`, `housing_areas`, `exploration_spots`, `transit_tips`, `community_groups`
- ranking scores: `support_coverage_score`, `belonging_score`, `cultural_fit_score`
- `best_weekend_outing`
- `subgraph` with normalized nodes and edges

### Deterministic Ranking Policy
Mentor score weights:
- shared country: `0.30`
- shared university: `0.25`
- need overlap: `0.25`
- trust/reputation score: `0.20`

Stage-aware matching can adjust category weights:
- newcomers: mentors, document tasks, arrival logistics
- settlers: peers, groups, events, social belonging
- locals: community leadership, mentoring, advanced city discovery

## 3. Markdown Graph Agent / Service

### Responsibility
Parse, validate, index, and query the Markdown knowledge graph.

### Inputs
- Markdown files under `data/graph/{city}/...`
- YAML frontmatter
- `[[wikilinks]]`

### Outputs
- normalized node list
- normalized edge list
- city/profile-filtered evidence bundle
- topologically sorted task chain
- validation report

### Validation Rules
- duplicate ids are errors
- broken `links_to`, `depends_on`, and wikilinks are errors
- task dependency cycles are errors
- missing required type fields are errors
- stale event/date claims must include verification language

## 4. Judge Agent (Plan Generation)

### Responsibility
Generate an ordered first-30-days plan from graph evidence through the selected AI provider.

### Provider Behavior
- Provider selected by `AI_PROVIDER` (`auto` prefers Gemini when key exists).
- On provider failure, return deterministic checklist fallback from the Markdown task graph.

### Hard Requirements
- Use evidence entities only; citation validation runs server-side.
- Preserve dependency order from `tasks_ordered`.
- Return JSON shape expected by `PlanGenerateResponse`.

### Output Schema Highlights
- `plan_title`
- `best_next_action`
- `steps[]` with `day_range`, `action`, `entities`, `dependency_reason`, `source_node_ids`
- `priority_contacts`, `warnings`, `confidence`, `fallback_used`, `llm_provider`

## 5. Cultural Bridge Agent

### Responsibility
Explain unfamiliar local terms in plain language using home-country context.

### Trigger Points
- User presses "Explain term" in Step 2
- User taps quick chips such as `security deposit`, `credit score`, `SSN`
- Future chat pre-seeds a message from the old drawer term

### Output Schema Highlights
- `term`
- `plain_explanation`
- `home_context_analogy`
- `common_mistakes[]`
- `what_to_do_next[]`
- `fallback_used`, `llm_provider`

## 6. Chat Agent

### Responsibility
Answer persistent user questions about US life, city setup, documents, and cultural context.

### Inputs
- current user profile from Neon Postgres when logged in
- last 10 chat messages from `chat_messages`
- relevant Markdown graph evidence for city/topic

### Outputs
- assistant message
- stored user/assistant message rows
- fallback response when providers fail

## 7. Fallback Rules
- If AI generation fails, return deterministic structured output, never empty text.
- If graph entities are sparse, return best available recommendations with warnings.
- For events/maps/transit details, keep disclaimer language that dates/routes must be independently verified.
- If Neon persistence is unavailable, public onboarding can still run using anonymous session evidence.
