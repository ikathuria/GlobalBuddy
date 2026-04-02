# GlobalBuddy Software Requirements Specification (SRS)

## 1. Introduction
### 1.1 Purpose
Define functional, non-functional, and interface requirements for GlobalBuddy.

### 1.2 Scope
GlobalBuddy captures student profile context, queries Neo4j for relevant matches/resources, and uses RocketRide to generate a personalized first-30-days survival plan.

### 1.3 Intended Audience
- Engineers
- Designers
- Hackathon teammates
- Judges and technical reviewers

## 2. Overall Description
### 2.1 Product Perspective
Web app with:
- React frontend + vis.js live graph visualization
- FastAPI backend orchestrator
- Neo4j AuraDB graph data source
- RocketRide AI plan and explanation generation

### 2.2 User Classes
- New international student
- Student mentor
- Demo administrator

### 2.3 Constraints
- Neo4j must be the primary database.
- RocketRide must drive at least one core intelligent workflow.
- Prototype must be stable for hackathon demo conditions.

## 3. Functional Requirements
- FR-1 Profile Input Capture
  - System shall accept country of origin, home city, destination university/city, needs, interests.
- FR-2 Mentor Matching
  - System shall return top 3 mentors ranked by shared background, university relevance, need fit, trust score.
- FR-3 Peer Discovery
  - System shall return nearby peers with relevance reasons.
- FR-4 Cultural Comfort Matching
  - System shall return culturally relevant restaurants and community events.
- FR-5 Graph Visualization
  - System shall display student-centered relationship graph and incremental match highlights.
- FR-6 Ordered Plan Generation
  - System shall generate a 30-day plan with ordered steps using dependency rules and graph evidence.
- FR-7 Cultural Bridge Explanations
  - System shall explain unfamiliar local terms by mapping to student home-country context.
- FR-8 Resource Recommendations
  - System shall include official offices/resources relevant to requested needs.
- FR-9 Explainability
  - Every plan step shall reference graph entities used (names/places/events/resources).
- FR-10 Fallback Behavior
  - If specific match types are unavailable, system shall provide closest alternatives and state confidence.

## 4. Non-Functional Requirements
- NFR-1 Performance
  - Core recommendations in 2-5 seconds under demo data size.
- NFR-2 Reliability
  - Hero demo flow should be stable and repeatable.
- NFR-3 Usability
  - First-time users should understand next action without onboarding.
- NFR-4 Maintainability
  - Agent logic, data access, and UI modules should be separable.
- NFR-5 Explainability
  - Responses should include match reasoning and source evidence.
- NFR-6 Accessibility
  - UI should support keyboard navigation and readable contrast.

## 5. Data Requirements
### 5.1 Core Entities
Student, Mentor, Peer, University, City, Neighborhood, Need, Task, Resource, Restaurant, Event, CulturalGroup, Country

### 5.2 Core Relationships
FROM_COUNTRY, STUDIES_AT, NEEDS_HELP_WITH, CAN_HELP_WITH, LIVES_NEAR, RECOMMENDED_FOR, OCCURS_IN, SERVES_CUISINE, PRECEDES, CONNECTED_TO

### 5.3 Ordering Logic
Task dependency graph shall encode prerequisite relationships (for example identity setup before banking readiness; banking readiness before rental commitment tasks).

## 6. External Interfaces
- UI interface via web frontend.
- Backend API endpoints defined in `docs/api-spec.md`.
- Neo4j interface via official driver and Cypher.
- RocketRide interface via HTTP API.

## 7. Core User Flow
1. Student submits profile.
2. Profile and Match Agent queries Neo4j and ranks matches.
3. Judge Agent composes ordered plan from graph evidence.
4. Cultural Bridge Agent provides on-demand term explanations.
5. Frontend renders graph, cards, and final survival timeline.

## 8. Acceptance Criteria
- AC-1 User can submit profile successfully.
- AC-2 Top 3 mentors are returned with reasons.
- AC-3 Nearby peers, restaurants, and events are returned.
- AC-4 Graph visualization renders matched entities and connections.
- AC-5 Final plan includes explicit names/places from graph data.
- AC-6 Ordering logic enforces dependency sequence.
- AC-7 Neo4j and RocketRide are visibly central and indispensable.
