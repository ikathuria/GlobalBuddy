# Globalदोस्त Neo4j Data Model

## 1. Primary node labels
- `Session`
- `StudentProfile`
- `Mentor`
- `Peer`
- `University`
- `Country`
- `City`
- `Need`
- `Task`
- `Resource`
- `Restaurant`
- `Event`
- `PlaceOfWorship`
- `GroceryStore`
- `HousingArea`
- `ExplorationSpot`
- `TransitTip`

## 2. Core relationship patterns
- `(:Session)-[:FOR_STUDENT]->(:StudentProfile)`
- `(:Mentor)-[:FROM_COUNTRY]->(:Country)`
- `(:Mentor)-[:ALUM_OF]->(:University)`
- `(:Mentor)-[:CAN_HELP_WITH]->(:Need)`
- `(:Peer)-[:STUDIES_AT]->(:University)`
- `(:Restaurant)-[:SERVES_CUISINE]->(:Country)`
- `(:Event)-[:RELEVANT_TO]->(:Country)`
- `(:Event)-[:OCCURS_IN]->(:City)`
- `(:Resource)-[:HELPS_WITH]->(:Need)`
- `(:Task)-[:PRECEDES]->(:Task)`
- `(:HousingArea)-[:NEAR_UNIVERSITY]->(:University)`
- `(:ExplorationSpot)-[:LOCATED_IN]->(:City)`
- `(:TransitTip)-[:GOOD_FOR]->(:City)`
- `(:PlaceOfWorship)-[:RELEVANT_TO]->(:Country)` (optional)
- `(:GroceryStore)-[:RELEVANT_TO]->(:Country)` (optional)

## 3. Key property highlights
- `Mentor`: `id`, `name`, `trust_score`, `languages`, `email`, `connect_hint`
- `Peer`: `id`, `name`, `university`, `neighborhood`, `email`, `connect_hint`
- `Event`: `id`, `name`, `category`, `start_time`, `location`, `notes`, `maps_query`, `maps_link`
- `Task`: `id`, `name`, `priority`, `estimated_day_window`
- Local place labels (`PlaceOfWorship`, `GroceryStore`, `HousingArea`, `ExplorationSpot`):
  - `id`, `name`, `address`, `neighborhood`, `maps_query`, `maps_link`, optional tag arrays
- `TransitTip`: `id`, `name`, `summary`, `route_hint`, `maps_link`

## 4. Ranking and scoring inputs
- Mentor ranking: shared country, shared university, need overlap, trust score.
- Local-fit ranking: profile token overlap against place/event tags.
- Aggregated API scores:
  - `support_coverage_score`
  - `belonging_score`
  - `cultural_fit_score`

## 5. Task dependency layer
Task ordering is encoded via `Task-[:PRECEDES]->Task` and transformed into ordered output for plan generation.

## 6. Seed guidance
Seed scripts should keep deterministic demo quality with:
- mentor and peer coverage for at least one hero university-city path
- task chain with clear prerequisite links
- local context entities with map query/link metadata
- event/resource notes that avoid claiming live schedule guarantees
