# Globalदोस्त Demo Runbook

## 1. Demo objective
Show a polished, low-friction arrival journey where graph evidence and AI reasoning are both visible and useful.

## 2. Recommended scenario
- Origin: India
- Home city: Bengaluru
- Destination: Illinois Institute of Technology, Chicago
- Needs: banking, housing, community
- Optional context: South Indian, Hindu, vegetarian

## 3. Pre-demo checklist
1. Run backend and frontend locally.
2. Verify `/health` and `/health/neo4j` are reachable.
3. Seed graph if Neo4j node count is zero.
4. Confirm one AI provider path is configured.

## 4. Live demo flow (5-7 minutes)
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
   - Use quick chip (for example `security deposit`) and show explanation drawer.
5. **Step 3: Explore Graph**
   - Switch categories (People, Events, Food, Housing, Tasks).
   - Open one person profile modal and show contact actions.
   - Focus a card in graph, show shortest path and node detail panel.
   - Open map link/preview for one location.

## 5. Returning-user variant
If `new_to_us=false` during profile setup:
- show that Step 2 is intentionally skipped
- proceed directly to Step 3 exploration

## 6. Key talking points
- Neo4j is the evidence engine (not passive storage).
- AI plan and term explanations are provider-backed but safely fall back when needed.
- Product minimizes overwhelm by sequencing actions and surfacing human context.

## 7. Fallback path
If provider call fails or is slow:
- show deterministic plan/bridge fallback behavior
- continue demo through Explore Graph and map-backed local recommendations

## 8. Demo close line
"You didn't come this far to figure it out alone."
