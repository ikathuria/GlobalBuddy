# Globalदोस्त API Specification (FastAPI)

## 1. API Conventions
- Base path: `/v1`
- Content type: `application/json`
- Health endpoints live at root: `/health`, `/health/providers`, `/health/graph`, `/health/db`
- Protected routes use `Authorization: Bearer <token>` when Neon Auth persistence is enabled

## 2. POST `/v1/profile/match`
Runs profile matching, local-intelligence ranking, and session creation from graph evidence.

### Request Example
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

### Response Shape
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
  "community_groups": [],
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

## 6. POST `/v1/chat/message`
Sends a chat message. Authenticated users sync chat history to Neon Postgres; public/no-DB sessions use in-memory history.

### Request
```json
{
  "session_id": "uuid",
  "message": "How do I open a bank account?"
}
```

### Response
```json
{
  "reply": "...",
  "fallback_used": false,
  "llm_provider": "gemini"
}
```

## 7. Progress Endpoints

### GET `/v1/progress/plan`
Requires `Authorization: Bearer <token>`.

```json
{
  "items": [
    { "task_id": "task_open_bank_account", "completed": true, "updated_at": "2026-06-03T12:00:00+00:00" }
  ]
}
```

### PUT `/v1/progress/plan/{task_id}`
Requires `Authorization: Bearer <token>`.

```json
{ "completed": true }
```

## 8. Document Endpoints

### GET `/v1/documents`
Requires `Authorization: Bearer <token>`.

```json
{
  "items": [
    { "doc_type": "ssn", "status": "in_progress", "updated_at": "2026-06-03T12:00:00+00:00" }
  ]
}
```

### PUT `/v1/documents/{doc_type}`
Requires `Authorization: Bearer <token>`.

```json
{ "status": "done" }
```

## 9. Auth Endpoints
- `GET /v1/auth/config`
- `GET /v1/auth/me`
- `GET /v1/auth/linkedin/profile`
- `POST /v1/auth/signup` returns `501`; use the Neon Auth frontend SDK on `/auth`
- `POST /v1/auth/login` returns `501`; use the Neon Auth frontend SDK on `/auth`

Auth is backed by Neon Auth. FastAPI verifies JWTs through the configured Neon Auth JWKS and resolves the app profile in Neon Postgres.

## 10. Health Endpoints

### GET `/health`
```json
{ "status": "ok" }
```

### GET `/health/providers`
```json
{
  "gemini": { "status": "ok", "latency_ms": 120 },
  "groq": { "status": "not_configured", "latency_ms": null },
  "anthropic": { "status": "not_configured", "latency_ms": null }
}
```

### GET `/health/graph` (Target)
```json
{
  "status": "ok",
  "source": "markdown",
  "node_count": 123,
  "edge_count": 456,
  "validation_errors": []
}
```

### GET `/health/db`
```json
{ "status": "ok" }
```

### GET `/health/neo4j` (Legacy)
May remain temporarily during migration for the existing Neo4j adapter.
