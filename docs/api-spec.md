# Globalदोस्त API Specification (FastAPI)

## 1. API conventions
- Base path: `/v1`
- Content type: `application/json`
- Health endpoints live at root (`/health`, `/health/neo4j`)

## 2. POST `/v1/profile/match`
Runs profile matching, local-intelligence ranking, and session creation.

### Request (example)
```json
{
  "full_name": "Priya Raman",
  "email": "priya@example.com",
  "country_of_origin": "India",
  "home_city": "Bengaluru",
  "target_university": "Illinois Institute of Technology",
  "target_city": "Chicago",
  "needs": ["banking", "housing", "community"],
  "interests": ["south indian food", "hackathons", "tech meetups"],
  "new_to_us": true,
  "cultural_background": "South Indian",
  "religion_or_observance": "Hindu",
  "diet": "vegetarian",
  "linkedin_url": "",
  "instagram_url": "",
  "other_social_url": ""
}
```

### Response (high-level shape)
```json
{
  "session_id": "uuid",
  "mentors_top3": [],
  "peers_nearby": [],
  "cultural_restaurants": [],
  "community_events": [],
  "resources": [],
  "places_of_worship": [],
  "grocery_stores": [],
  "housing_areas": [],
  "exploration_spots": [],
  "transit_tips": [],
  "evidence_bundle": {},
  "subgraph": {
    "nodes": [],
    "edges": []
  },
  "support_coverage_score": 0.0,
  "belonging_score": 0.0,
  "cultural_fit_score": 0.0,
  "best_weekend_outing": ""
}
```

## 3. POST `/v1/plan/generate`
Generates first-30-days plan using session evidence and selected provider.

### Request
```json
{
  "session_id": "uuid",
  "student_profile": {},
  "evidence_bundle": {}
}
```

### Response
```json
{
  "plan_title": "Your First 30 Days",
  "best_next_action": "Open a bank account with required documents.",
  "steps": [
    {
      "day_range": "Day 1-3",
      "action": "...",
      "entities": ["..."],
      "dependency_reason": "...",
      "source_node_ids": ["mentor_12", "resource_4"]
    }
  ],
  "priority_contacts": ["..."],
  "warnings": [],
  "confidence": 0.91,
  "fallback_used": false,
  "llm_provider": "gemini"
}
```

## 4. POST `/v1/bridge/explain`
Returns plain-language cultural explanation for a term.

### Request
```json
{
  "session_id": "uuid",
  "term": "security deposit",
  "home_country": "India",
  "context": "off-campus rental and banking setup"
}
```

### Response
```json
{
  "term": "security deposit",
  "plain_explanation": "...",
  "home_context_analogy": "...",
  "common_mistakes": ["..."],
  "what_to_do_next": ["..."],
  "fallback_used": false,
  "llm_provider": "gemini"
}
```

## 5. GET `/v1/graph/subgraph?session_id=...`
Returns session-scoped graph for UI visualization.

### Response
```json
{
  "nodes": [],
  "edges": [],
  "highlights": []
}
```

## 6. GET `/health`
```json
{ "status": "ok" }
```

## 7. GET `/health/neo4j`
```json
{
  "status": "ok",
  "node_count": 123,
  "seed_command": null
}
```

When `node_count` is `0`, `seed_command` includes the backend seed command string.
