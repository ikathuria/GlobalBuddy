# GlobalBuddy Agent Specifications

## 1. Shared Agent Contract
Each agent receives:
- `session_id`
- `student_profile`
- `evidence_bundle` (if available)
- `tool_results`

Each agent returns:
- `status`
- `output`
- `confidence`
- `trace_ids`

## 2. Profile and Match Agent
### Responsibility
Understand student profile and retrieve top matches via Neo4j.

### Tools
- `query_graph(cypher, params)`
- `rank_matches(candidates, weights)`
- `fetch_subgraph(student_id, matched_ids)`

### Required Output
- Top 3 mentors
- Nearby peers
- Cultural restaurants
- Upcoming community events
- Match reasons and confidence for each item

### Deterministic Ranking Policy
Recommended default weights:
- shared country: 0.30
- shared university: 0.25
- need fit overlap: 0.25
- trust score: 0.20

## 3. Judge Agent
### Responsibility
Generate warm, specific, ordered "First 30 Days Survival Plan" from graph evidence.

### Tools
- `get_task_dependencies(needs)`
- `compose_plan_with_rocketride(evidence_bundle, constraints)`

### Hard Requirements
- Must cite actual names/places/events from evidence bundle.
- Must respect dependency ordering from task graph.
- Must avoid generic or unverifiable recommendations.

### Output Schema
- `plan_title`
- `steps[]` with day range, action, entities, dependency reason
- `priority_contacts[]`
- `confidence` and `warnings[]`

## 4. Cultural Bridge Agent
### Responsibility
Explain unfamiliar local terms using home-country analogies.

### Tools
- `compose_explanation_with_rocketride(term, home_country, context)`

### Trigger
Called when student clicks "Explain this" or Judge flags terms likely unfamiliar.

### Output Schema
- `term`
- `plain_explanation`
- `home_context_analogy`
- `common_mistakes`
- `what_to_do_next`

## 5. Error and Fallback Rules
- If fewer than 3 mentors, return best available plus explicit fallback reason.
- If events are missing, return evergreen cultural groups/resources.
- If AI call fails, return structured deterministic checklist from task graph.
