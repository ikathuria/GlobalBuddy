# GlobalBuddy Business Requirements Document (BRD)

## 1. Product Vision
GlobalBuddy helps international students navigate their first 30 days in a new US city with personalized, graph-grounded guidance.

Motto: "You didn't come this far to figure it out alone."

## 2. Problem Statement
International students face high-friction first-week tasks with low context:
- They do not know which action comes first.
- They do not know who to trust.
- They do not know where to find culturally familiar support.

This causes avoidable stress, delays, and costly mistakes.

## 3. Target Users
- Primary: New international students in US universities.
- Secondary: Existing student mentors.
- Tertiary: Hackathon judges and reviewers evaluating the prototype.

## 4. Business Goals
- Reduce first-month uncertainty with a concrete action plan.
- Increase trust by linking students to relevant mentors and peers.
- Improve belonging through cultural comfort recommendations (food and events).
- Demonstrate deep Neo4j + RocketRide integration for hackathon criteria.

## 5. Value Proposition
GlobalBuddy combines:
- Neo4j relationship intelligence to discover trusted, relevant connections.
- RocketRide AI reasoning to convert graph evidence into ordered next steps.

Output is not generic tips. Output is a named, local, ordered survival plan.

## 6. Success Metrics (Hackathon MVP)
- A student can submit profile input and receive results end-to-end.
- Top 3 mentor recommendations include clear match reasons.
- Nearby peers, cultural restaurants, and upcoming events are returned.
- A graph view renders links from student to matched entities.
- The final 30-day plan references actual names/places from graph data.
- Judges can clearly see Neo4j and RocketRide as central to the workflow.

## 7. In Scope (MVP)
- One polished hero journey (India student -> US university).
- Core needs: banking, housing, visa/admin setup.
- Three core agents:
  - Profile and Match Agent
  - Judge Agent
  - Cultural Bridge Agent
- React command center with live graph and recommendation panels.

## 8. Out of Scope (MVP)
- Full production onboarding and account management.
- High-scale multi-tenant architecture.
- Complete legal advice coverage for all visa classes.
- Nationwide data completeness for all US cities.

## 9. Risks and Mitigations
- Sparse data in some cities.
  - Mitigation: curated seed pack and deterministic demo scenario.
- Hallucinated AI output.
  - Mitigation: evidence-only prompt policy with entity citation.
- Inconsistent recommendation quality.
  - Mitigation: explicit scoring policy and deterministic ranking fields.

## 10. Hackathon Requirement Alignment
- Neo4j as primary database: yes, all matching and dependency logic are graph-backed.
- RocketRide as core intelligent feature: yes, plan generation and cultural explanation rely on it.
- Deep integration: yes, RocketRide consumes structured evidence produced by Neo4j queries.
