# Globalदोस्त Demo Runbook

## 1. Demo Objective
Show a polished, low-friction arrival journey where graph evidence and AI reasoning are both visible and useful.

## 2. Recommended Scenario
- Origin: India
- Home city: Bengaluru
- Destination: Illinois Institute of Technology, Chicago
- Needs: banking, housing, community
- Optional context: South Indian, Hindu, vegetarian

## 3. Pre-Demo Checklist
1. Run backend and frontend locally.
2. Verify `/health` and provider health are reachable.
3. Verify graph-source health:
   - target: `/health/graph`
   - legacy during migration: `/health/neo4j`
4. Confirm one AI provider path is configured.
5. If demoing the target architecture, run Markdown graph validation before opening the app.

## 4. Live Demo Flow (5-7 Minutes)
1. **Landing + status**
   - Show Globalदोस्त brand, hero copy, and live status pills.
2. **Step 1: Profile**
   - Walk through wizard tabs and smart starter defaults.
   - Submit profile and highlight success banner.
3. **Step 2: AI Plan**
   - Generate plan.
   - Highlight best next action, week grouping, and task completion toggle.
   - Click "Why this matters culturally" on one step.
4. **Cultural Bridge**
   - Use quick chip such as `security deposit` and show explanation drawer.
5. **Step 3: Explore Graph**
   - Switch categories: People, Events, Food, Housing, Tasks, and later Groups.
   - Open one person profile modal and show contact actions.
   - Focus a card in graph, show shortest path and node detail panel.
   - Open map link/preview for one location.

## 5. Returning-User Variant
If `new_to_us=false` during profile setup:
- show that Step 2 is intentionally skipped
- proceed directly to Step 3 exploration

## 6. Key Talking Points
- The Markdown knowledge graph is the evidence engine for the MVP: editable, versioned, and easy to validate.
- Neon Auth/Postgres handles private accounts and persistence without spreading user data into graph files.
- AI plan and term explanations are provider-backed but safely fall back when needed.
- Product minimizes overwhelm by sequencing actions and surfacing human context.
- Neo4j remains a possible later upgrade, not a dependency for the MVP direction.

## 7. Fallback Path
If provider call fails or is slow:
- show deterministic plan/bridge fallback behavior
- continue demo through Explore Graph and map-backed local recommendations

If graph validation fails:
- fix Markdown frontmatter or broken links before demo
- use the legacy Neo4j adapter only if the Markdown migration is not ready yet

## 8. Demo Close Line
"You didn't come this far to figure it out alone."
