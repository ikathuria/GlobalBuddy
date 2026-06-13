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
  "arrival_date": "2026-02-15",
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
  "user_stage": "settler",
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

## 6b. POST `/v1/chat/stream`
Same request body as `/v1/chat/message`, but the response is Server-Sent Events (`text/event-stream`). Each `data:` line is a JSON event:

```
data: {"type": "session", "session_id": "uuid"}
data: {"type": "delta", "text": "partial reply text"}
data: {"type": "done", "reply": "full reply", "session_id": "uuid", "fallback_used": false}
```

`session` arrives first, `delta` repeats per chunk, and `done` always arrives last — including on provider failure, where `fallback_used` is `true` and `reply` carries whatever partial or fallback text was streamed. Authenticated users get both messages persisted to Neon on `done`. Providers without streaming support send the entire reply as a single `delta`.

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

## 8b. Social Endpoints (M11)
All require `Authorization: Bearer <token>`. Requests target Markdown graph entities (seed mentors/peers) identified by node id and are recorded against the requester in `social_requests`.

### POST `/v1/social/connect`
Records a connection request to a peer. `target_name`/`target_role` fall back to the graph node when omitted.

```json
{ "target_node_id": "peer_arjun_mehta", "target_name": "Arjun Mehta", "target_role": "Peer", "message": "" }
```

Returns the stored request:

```json
{
  "id": "uuid",
  "kind": "connection",
  "target_node_id": "peer_arjun_mehta",
  "target_name": "Arjun Mehta",
  "target_role": "Peer",
  "status": "pending",
  "email_sent": false,
  "created_at": "2026-06-12T00:00:00+00:00"
}
```

### POST `/v1/social/intro-request`
Records a mentor intro request and sends a templated email to the mentor via Resend. The mentor's email address is read from the graph node server-side and is **never** returned to the client. `404` if the mentor node id is unknown. `email_sent` is `false` when `RESEND_API_KEY` is unset or a duplicate request already existed.

```json
{ "mentor_node_id": "mentor_priya_shah", "message": "I'd love advice on banking." }
```

```json
{ "id": "uuid", "kind": "intro", "target_name": "Priya Shah", "status": "pending", "email_sent": true, "created_at": "2026-06-12T00:00:00+00:00" }
```

### GET `/v1/social/requests`
Lists the current user's connection and intro requests, newest first.

```json
{ "items": [ { "id": "uuid", "kind": "intro", "target_name": "Priya Shah", "status": "pending", "email_sent": true, "created_at": "..." } ] }
```

## 8c. Feed Endpoints (M12)
Browsing is public; saving requires `Authorization: Bearer <token>`.

### GET `/v1/feed`
Query: `city` (default `Chicago`), `category` (`guide|event|food|tip`), `offset`, `limit` (1–50), `tags` (comma-separated). Merges Markdown graph items with published Neon `content_items`. For logged-in users each item carries `saved`.

```json
{
  "items": [
    { "id": "guide_cta_ventra_basics", "source": "markdown", "type": "guide", "title": "...", "body": "...", "city": "Chicago", "tags": ["transit"], "maps_query": "", "maps_link": "", "saved": false }
  ],
  "next_offset": 9
}
```

### POST `/v1/feed/save`
`{ "content_id": "guide_cta_ventra_basics", "content_source": "markdown" }` → `204`.

### DELETE `/v1/feed/save/{content_id}?content_source=markdown`
→ `204`.

### GET `/v1/feed/saved`
Returns the user's saved items resolved against the feed corpus.

## 9. Auth Endpoints
- `GET /v1/auth/config`
- `GET /v1/auth/me`
- `PATCH /v1/auth/me/stage`
- `GET /v1/auth/linkedin/profile`
- `POST /v1/auth/signup` returns `501`; use the Neon Auth frontend SDK on `/auth`
- `POST /v1/auth/login` returns `501`; use the Neon Auth frontend SDK on `/auth`

Auth is backed by Neon Auth. FastAPI verifies JWTs through the configured Neon Auth JWKS and resolves the app profile in Neon Postgres.

### PATCH `/v1/auth/me/stage`
Requires `Authorization: Bearer <token>`. Manually advances the user journey stage to `settler` or `local`; the endpoint does not allow mentor opt-in because that is handled by the mentor flow.

```json
{ "stage": "settler" }
```

```json
{
  "profile": {
    "stage": "settler",
    "arrival_date": "2026-02-15"
  }
}
```

### GET `/v1/auth/linkedin/profile`
Requires `Authorization: Bearer <token>`. Returns claim-derived prefill fields and never writes profile data by itself.

```json
{
  "source": "linkedin",
  "full_name": "Priya Raman",
  "email": "priya@example.com",
  "linkedin_url": "https://www.linkedin.com/in/priya",
  "country_of_origin": "",
  "target_university": ""
}
```

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
