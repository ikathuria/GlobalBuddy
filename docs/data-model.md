# Globalदोस्त Data Model

## 1. Data Ownership
Globalदोस्त uses two data stores in the target MVP:

- **Markdown knowledge graph:** public/static city knowledge stored in Git.
- **Neon Postgres:** private/dynamic user and product data.

Private user data must never be committed to Markdown.

## 2. Markdown Knowledge Graph

### Folder Layout
```text
data/graph/
  chicago/
    mentors/
    universities/
    tasks/
    places/
    events/
    groups/
    guides/
  boston/
  new-york/
```

### File Shape
Each graph node is a Markdown file with YAML frontmatter and optional `[[wikilinks]]` in the body.

```md
---
id: task_apply_ssn
type: Task
title: Apply for SSN
city: Chicago
category: document
stage: newcomer
needs:
  - employment
  - documents
depends_on:
  - task_retrieve_i94
links_to:
  - guide_ssn
  - place_social_security_office_chicago
---

# Apply for SSN

Bring your passport, I-20, I-94, and employment eligibility letter.

Related: [[I-94]], [[Social Security Office]], [[Bank Account]]
```

## 3. Markdown Node Types
- `Mentor`
- `Peer`
- `University`
- `Country`
- `City`
- `Need`
- `Task`
- `Guide`
- `Resource`
- `Restaurant`
- `Event`
- `PlaceOfWorship`
- `GroceryStore`
- `HousingArea`
- `ExplorationSpot`
- `TransitTip`
- `CommunityGroup`
- `PreArrivalChecklist` — city-agnostic checklist items under `data/graph/common/pre-arrival/`; no `city` field required. Served by `GET /v1/pre-arrival/checklist` and kept out of plan task ordering.

## 4. Markdown Relationship Sources
Relationships are generated from:

- `depends_on` frontmatter for ordered task dependencies.
- `links_to` frontmatter for explicit typed edges.
- `[[wikilinks]]` in the Markdown body for Obsidian-style related edges.
- Normalized tag overlap for scoring relationships, such as shared `city`, `country_tags`, `university_tags`, `needs`, `diet_tags`, and `religion_tags`.

## 5. Graph Scoring Inputs
- Mentor ranking: shared country, shared university, need overlap, languages, stage fit, trust/reputation score.
- Local-fit ranking: profile token overlap against place/event/group tags.
- Stage fit: `arrival_date` maps to newcomer under 90 days, settler from 90 to 364 days, and local from 365 days onward; mentor is never automatic.
- Task ordering: `depends_on` edges are topologically sorted before plan generation.
- Aggregated API scores:
  - `support_coverage_score`
  - `belonging_score`
  - `cultural_fit_score`

## 6. Neon Postgres Tables

### Identity and Profile
- `user_profiles`: `id`, `auth_user_id`, `full_name`, `email`, `country_of_origin`, `target_university`, `target_city`, `stage`, `arrival_date`, `created_at`, `updated_at`

`auth_user_id` references the user identity synced by Neon Auth.
`stage` is inferred from `arrival_date` during profile matching and can move forward manually through `PATCH /v1/auth/me/stage`; automatic updates do not move a user backward.

### Progress and Documents
- `plan_progress`: `user_id`, `task_id`, `completed`, `updated_at`
- `user_documents`: `user_id`, `doc_type`, `status`, `updated_at`

### App Sessions
- `app_sessions`: `session_id`, `payload`, `expires_at`, `created_at`, `updated_at`

Profile match evidence and subgraphs are cached here for 24 hours by default so plan and graph routes can survive API process restarts.

### Chat
- `chat_messages`: `id`, `user_id`, `session_id`, `role`, `content`, `created_at`

### Social
- `connections`: `id`, `requester_id`, `recipient_id`, `status`, `created_at`, `updated_at`
- `intro_requests`: `id`, `requester_id`, `mentor_id`, `status`, `message`, `created_at`, `updated_at`

### Feed and Saved Content
- `content_items`: `id`, `type`, `title`, `body`, `city`, `tags`, `author_id`, `published_at`
- `saved_content`: `user_id`, `content_id`, `content_source`, `created_at`

### Mentors
- `mentor_profiles`: `user_id`, `expertise`, `availability`, `bio`, `response_rate`, `intro_count`, `rating`, `opted_in_at`
- `mentor_ratings`: `id`, `mentor_id`, `reviewer_id`, `rating`, `comment`, `created_at`

### Notifications
- `notifications`: `id`, `user_id`, `type`, `title`, `body`, `read`, `created_at`

## 7. Validation Rules
- Every Markdown node must have a globally unique `id`.
- Every Markdown node must have `type`, `title`, and `city` when city-specific.
- `depends_on` and `links_to` targets must exist.
- Task dependency graph must be acyclic.
- Map-bearing nodes should include `address`, `lat`, `lng`, or `maps_query`.
- Time-sensitive nodes must include verification/disclaimer copy.

## 8. Legacy Neo4j Notes
The existing Neo4j/Cypher seed data remains useful as migration source material. It is not the target MVP source of truth after the Markdown graph engine is implemented.
