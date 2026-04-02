# GlobalBuddy API Specification (FastAPI)

## 1. API Conventions
- Base path: `/v1`
- Content type: `application/json`
- Error envelope:
```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Human readable message",
    "trace_id": "uuid"
  }
}
```

## 2. POST /v1/profile/match
Run profile analysis and graph matching.

Request:
```json
{
  "country_of_origin": "India",
  "home_city": "Bengaluru",
  "target_university": "Illinois Institute of Technology",
  "target_city": "Chicago",
  "needs": ["banking", "housing", "community"],
  "interests": ["south indian food", "hackathons", "Luma events"]
}
```

Response:
```json
{
  "session_id": "uuid",
  "mentors_top3": [],
  "peers_nearby": [],
  "cultural_restaurants": [],
  "community_events": [],
  "resources": [],
  "subgraph": {
    "nodes": [],
    "edges": []
  }
}
```

## 3. POST /v1/plan/generate
Generate ordered survival plan from evidence bundle.

Request:
```json
{
  "session_id": "uuid",
  "student_profile": {},
  "evidence_bundle": {}
}
```

Response:
```json
{
  "plan_title": "Your First 30 Days in Chicago",
  "steps": [
    {
      "day_range": "Day 1-3",
      "action": "Contact mentor A and visit office B",
      "entities": ["Mentor A", "Office B"],
      "dependency_reason": "Documentation readiness before account setup",
      "source_node_ids": ["mentor_12", "resource_4"]
    }
  ],
  "priority_contacts": [],
  "warnings": [],
  "confidence": 0.91
}
```

## 4. POST /v1/bridge/explain
Explain local term in student context.

Request:
```json
{
  "session_id": "uuid",
  "term": "security deposit",
  "home_country": "India",
  "context": "off-campus rental"
}
```

Response:
```json
{
  "term": "security deposit",
  "plain_explanation": "...",
  "home_context_analogy": "...",
  "common_mistakes": ["..."],
  "what_to_do_next": ["..."]
}
```

## 5. GET /v1/graph/subgraph
Fetch graph nodes/edges for frontend render.

Query params:
- `session_id`

Response:
```json
{
  "nodes": [],
  "edges": [],
  "highlights": []
}
```

## 6. GET /v1/events/upcoming
Fetch filtered events.

Query params:
- `city`
- `country_context`
- `university`

## 7. Latency Targets
- `/profile/match`: 2-5s under demo load.
- `/plan/generate`: <=6s under demo load.
- `/bridge/explain`: <=3s under demo load.
