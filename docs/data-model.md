# GlobalBuddy Neo4j Data Model

## 1. Node Labels
- Student
- Mentor
- Peer
- University
- Country
- City
- Neighborhood
- Need
- Task
- Resource
- Restaurant
- Event
- CulturalGroup

## 2. Relationship Types
- (:Student)-[:FROM_COUNTRY]->(:Country)
- (:Student)-[:STUDIES_AT]->(:University)
- (:Student)-[:NEEDS_HELP_WITH]->(:Need)
- (:Mentor)-[:ALUM_OF]->(:University)
- (:Mentor)-[:FROM_COUNTRY]->(:Country)
- (:Mentor)-[:CAN_HELP_WITH]->(:Need)
- (:Peer)-[:STUDIES_AT]->(:University)
- (:Peer)-[:LIVES_NEAR]->(:Neighborhood)
- (:Restaurant)-[:SERVES_CUISINE]->(:Country)
- (:Event)-[:RELEVANT_TO]->(:Country)
- (:Event)-[:OCCURS_IN]->(:City)
- (:Resource)-[:HELPS_WITH]->(:Need)
- (:Task)-[:PRECEDES]->(:Task)

## 3. Key Properties
- Mentor: `id`, `name`, `trust_score`, `response_rate`, `languages`
- Peer: `id`, `name`, `university`, `neighborhood`
- Restaurant: `id`, `name`, `price_level`, `distance_km`
- Event: `id`, `name`, `start_time`, `location`, `category`
- Task: `id`, `name`, `priority`, `estimated_day_window`

## 4. Constraints and Indexes (MVP)
```cypher
CREATE CONSTRAINT student_id IF NOT EXISTS FOR (n:Student) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT mentor_id IF NOT EXISTS FOR (n:Mentor) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT peer_id IF NOT EXISTS FOR (n:Peer) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT task_id IF NOT EXISTS FOR (n:Task) REQUIRE n.id IS UNIQUE;
CREATE INDEX mentor_country IF NOT EXISTS FOR (n:Mentor) ON (n.country_code);
CREATE INDEX event_time IF NOT EXISTS FOR (n:Event) ON (n.start_time);
```

## 5. Ranking Inputs
Mentor ranking score uses weighted fields:
- Shared country match
- Shared university match
- Need coverage overlap
- Trust score
- Distance or accessibility

## 6. Task Dependency Layer
Use `Task-[:PRECEDES]->Task` to enforce ordering.
- Example chain:
  - Identity and documentation readiness
  - Banking setup
  - Rental commitment actions

## 7. Seed Data Guidance
Use curated synthetic+realistic data for deterministic demo quality:
- 1 hero university + 2 secondary universities
- 5 source countries
- 40 to 60 mentors/peers combined
- 20 to 40 events
- 20 to 40 restaurants/resources
