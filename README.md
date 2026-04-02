# GlobalBuddy

GlobalBuddy is an agentic platform for international students arriving in a new US city.

Motto: "You didn't come this far to figure it out alone."

## What It Does
- Matches students with relevant mentors and peers.
- Recommends culturally familiar food and community events.
- Generates a personalized, ordered "First 30 Days Survival Plan".
- Explains unfamiliar local concepts through home-country context.

## Core Stack
- Neo4j AuraDB (primary graph database)
- RocketRide AI (agent reasoning and generation)
- FastAPI (backend orchestration)
- React + vis.js (frontend command center and graph visualization)

## Agent Pipeline
1. Profile and Match Agent queries Neo4j and ranks top matches.
2. Judge Agent composes an ordered, evidence-grounded survival plan.
3. Cultural Bridge Agent explains confusing concepts in familiar context.

## Documentation
- [BRD](./docs/BRD.md)
- [SRS](./docs/SRS.md)
- [Architecture](./docs/architecture.md)
- [Data Model](./docs/data-model.md)
- [Agents Spec](./docs/agents-spec.md)
- [API Spec](./docs/api-spec.md)
- [Prompt Spec](./docs/prompt-spec.md)
- [Demo Runbook](./docs/demo-runbook.md)

## Hackathon Focus
This repository is intentionally optimized for one polished hero journey to maximize clarity, reliability, and judging impact.
