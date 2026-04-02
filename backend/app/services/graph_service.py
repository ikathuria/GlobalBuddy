from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from app.config import Settings
from app.models import GraphEdge, GraphNode, GraphSubgraph
from app.services.ranking_service import mentor_score, normalize_text_list


logger = logging.getLogger(__name__)


MENTOR_QUERY = """
MATCH (m:Mentor)-[:ALUM_OF]->(u:University)
WHERE toLower(u.name) = toLower($target_university)
OPTIONAL MATCH (m)-[:FROM_COUNTRY]->(country:Country)
OPTIONAL MATCH (m)-[:CAN_HELP_WITH]->(need:Need)
WITH m, country, collect(DISTINCT toLower(need.name)) AS mentor_need_names
RETURN
  m.id AS id,
  m.name AS name,
  coalesce(m.trust_score, 0.0) AS trust_score,
  coalesce(m.response_rate, 0.0) AS response_rate,
  coalesce(m.languages, []) AS languages,
  CASE WHEN country.code = $country_code THEN true ELSE false END AS shared_country,
  size([n IN mentor_need_names WHERE n IN $needs]) AS need_overlap_count
"""


MENTOR_FALLBACK_QUERY = """
MATCH (m:Mentor)
OPTIONAL MATCH (m)-[:FROM_COUNTRY]->(country:Country)
OPTIONAL MATCH (m)-[:CAN_HELP_WITH]->(need:Need)
WITH m, country, collect(DISTINCT toLower(need.name)) AS mentor_need_names
RETURN
  m.id AS id,
  m.name AS name,
  coalesce(m.trust_score, 0.0) AS trust_score,
  coalesce(m.response_rate, 0.0) AS response_rate,
  coalesce(m.languages, []) AS languages,
  CASE WHEN country.code = $country_code THEN true ELSE false END AS shared_country,
  size([n IN mentor_need_names WHERE n IN $needs]) AS need_overlap_count
"""


PEER_QUERY = """
MATCH (p:Peer)-[:STUDIES_AT]->(u:University)
WHERE toLower(u.name) = toLower($target_university)
RETURN
  p.id AS id,
  p.name AS name,
  p.neighborhood AS neighborhood
ORDER BY p.name ASC
LIMIT 6
"""


RESTAURANT_QUERY = """
MATCH (r:Restaurant)-[:SERVES_CUISINE]->(c:Country)
WHERE c.code = $country_code
RETURN
  r.id AS id,
  r.name AS name,
  r.distance_km AS distance_km,
  r.price_level AS price_level
ORDER BY coalesce(r.distance_km, 999.0) ASC, r.name ASC
LIMIT 6
"""


EVENT_QUERY = """
MATCH (e:Event)-[:OCCURS_IN]->(city:City)
WHERE toLower(city.name) = toLower($target_city)
MATCH (e)-[:RELEVANT_TO]->(country:Country)
WHERE country.code = $country_code OR country.code = 'US'
RETURN DISTINCT
  e.id AS id,
  e.name AS name,
  e.start_time AS start_time,
  e.location AS location,
  e.category AS category
ORDER BY e.start_time ASC
LIMIT 6
"""


RESOURCE_QUERY = """
UNWIND $needs AS need_name
MATCH (need:Need)
WHERE toLower(need.name) = need_name
MATCH (resource:Resource)-[:HELPS_WITH]->(need)
RETURN DISTINCT
  resource.id AS id,
  resource.name AS name,
  resource.type AS type,
  resource.url AS url
ORDER BY resource.name ASC
LIMIT 6
"""


COUNTRY_CODE_QUERY = """
MATCH (c:Country)
WHERE toLower(c.name) = toLower($country_value) OR toUpper(c.code) = toUpper($country_value)
RETURN c.code AS code
LIMIT 1
"""


UPSERT_SESSION_QUERY = """
MERGE (session:Session {id: $session_id})
ON CREATE SET session.created_at = datetime()
SET
  session.updated_at = datetime(),
  session.country_of_origin = $country_of_origin,
  session.home_city = $home_city,
  session.target_university = $target_university,
  session.target_city = $target_city,
  session.needs = $needs,
  session.interests = $interests
"""


LINK_MENTORS_QUERY = """
MATCH (session:Session {id: $session_id})
UNWIND $rows AS row
MERGE (mentor:Mentor {id: row.id})
ON CREATE SET mentor.name = row.name
SET mentor.name = coalesce(mentor.name, row.name)
MERGE (session)-[rel:MATCHED_MENTOR]->(mentor)
SET
  rel.score = coalesce(row.score, 0.0),
  rel.trust_score = coalesce(row.trust_score, 0.0),
  rel.response_rate = coalesce(row.response_rate, 0.0),
  rel.match_reasons = coalesce(row.match_reasons, []),
  rel.updated_at = datetime()
"""


LINK_PEERS_QUERY = """
MATCH (session:Session {id: $session_id})
UNWIND $rows AS row
MERGE (peer:Peer {id: row.id})
ON CREATE SET peer.name = row.name
SET
  peer.name = coalesce(peer.name, row.name),
  peer.neighborhood = coalesce(row.neighborhood, peer.neighborhood)
MERGE (session)-[rel:MATCHED_PEER]->(peer)
SET rel.updated_at = datetime()
"""


LINK_RESTAURANTS_QUERY = """
MATCH (session:Session {id: $session_id})
UNWIND $rows AS row
MERGE (restaurant:Restaurant {id: row.id})
ON CREATE SET restaurant.name = row.name
SET
  restaurant.name = coalesce(restaurant.name, row.name),
  restaurant.distance_km = coalesce(row.distance_km, restaurant.distance_km),
  restaurant.price_level = coalesce(row.price_level, restaurant.price_level)
MERGE (session)-[rel:MATCHED_RESTAURANT]->(restaurant)
SET rel.updated_at = datetime()
"""


LINK_EVENTS_QUERY = """
MATCH (session:Session {id: $session_id})
UNWIND $rows AS row
MERGE (event:Event {id: row.id})
ON CREATE SET event.name = row.name
SET
  event.name = coalesce(event.name, row.name),
  event.start_time = coalesce(row.start_time, event.start_time),
  event.location = coalesce(row.location, event.location),
  event.category = coalesce(row.category, event.category)
MERGE (session)-[rel:MATCHED_EVENT]->(event)
SET rel.updated_at = datetime()
"""


LINK_RESOURCES_QUERY = """
MATCH (session:Session {id: $session_id})
UNWIND $rows AS row
MERGE (resource:Resource {id: row.id})
ON CREATE SET resource.name = row.name
SET
  resource.name = coalesce(resource.name, row.name),
  resource.type = coalesce(row.type, resource.type),
  resource.url = coalesce(row.url, resource.url)
MERGE (session)-[rel:MATCHED_RESOURCE]->(resource)
SET rel.updated_at = datetime()
"""


UPSERT_PLAN_QUERY = """
MATCH (session:Session {id: $session_id})
MERGE (plan:GeneratedPlan {id: $plan_id})
ON CREATE SET plan.created_at = datetime()
SET
  plan.updated_at = datetime(),
  plan.plan_title = $plan_title,
  plan.priority_contacts = $priority_contacts,
  plan.warnings = $warnings,
  plan.confidence = $confidence
MERGE (session)-[:HAS_PLAN]->(plan)
"""


CLEAR_PLAN_STEPS_QUERY = """
MATCH (:GeneratedPlan {id: $plan_id})-[rel:HAS_STEP]->(step:GeneratedPlanStep)
DELETE rel
WITH step
DETACH DELETE step
"""


UPSERT_PLAN_STEPS_QUERY = """
MATCH (plan:GeneratedPlan {id: $plan_id})
UNWIND $steps AS step
CREATE (plan_step:GeneratedPlanStep {
  id: step.id,
  day_range: step.day_range,
  action: step.action,
  entities: step.entities,
  dependency_reason: step.dependency_reason,
  source_node_ids: step.source_node_ids
})
MERGE (plan)-[rel:HAS_STEP]->(plan_step)
SET rel.position = step.position
"""


UPSERT_BRIDGE_QUERY = """
MATCH (session:Session {id: $session_id})
MERGE (bridge:BridgeExplanation {id: $bridge_id})
ON CREATE SET bridge.created_at = datetime()
SET
  bridge.updated_at = datetime(),
  bridge.term = $term,
  bridge.context = $context,
  bridge.home_country = $home_country,
  bridge.plain_explanation = $plain_explanation,
  bridge.home_context_analogy = $home_context_analogy,
  bridge.common_mistakes = $common_mistakes,
  bridge.what_to_do_next = $what_to_do_next
MERGE (session)-[:HAS_BRIDGE_EXPLANATION]->(bridge)
"""


@dataclass
class ProfileInput:
    country_of_origin: str
    home_city: str
    target_university: str
    target_city: str
    needs: list[str]
    interests: list[str]


class GraphService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._driver = None
        if settings.neo4j_enabled:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
            )

    @property
    def enabled(self) -> bool:
        return self._driver is not None

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()

    def _run_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict]:
        if self._driver is None:
            raise RuntimeError("Neo4j is not configured.")
        with self._driver.session(database=self._settings.neo4j_database) as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def _write_query(self, query: str, params: dict[str, Any] | None = None) -> None:
        if self._driver is None:
            return
        with self._driver.session(database=self._settings.neo4j_database) as session:
            session.run(query, params or {})

    def _resolve_country_code(self, country_of_origin: str) -> str:
        country_value = (country_of_origin or "").strip()
        if not country_value:
            return "US"

        try:
            rows = self._run_query(COUNTRY_CODE_QUERY, {"country_value": country_value})
            if rows:
                return rows[0]["code"]
        except Neo4jError:
            return "US"

        if len(country_value) == 2:
            return country_value.upper()
        return "US"

    def profile_match(self, payload: ProfileInput) -> dict[str, Any]:
        if not self.enabled:
            return self._demo_profile_match(payload)

        try:
            normalized_needs = normalize_text_list(payload.needs)
            country_code = self._resolve_country_code(payload.country_of_origin)
            params = {
                "target_university": payload.target_university,
                "target_city": payload.target_city,
                "country_code": country_code,
                "needs": normalized_needs,
            }

            mentors = self._rank_mentors(params, need_count=len(normalized_needs))
            peers = self._run_query(PEER_QUERY, params)
            restaurants = self._run_query(RESTAURANT_QUERY, params)
            events = self._run_query(EVENT_QUERY, params)
            resources = self._run_query(RESOURCE_QUERY, params)
        except Neo4jError as exc:
            # Keep the API usable in local dev even if Neo4j is unreachable or misconfigured.
            logger.warning("Neo4j profile match failed, falling back to demo mode: %s", exc)
            return self._demo_profile_match(payload)

        return {
            "mentors_top3": mentors,
            "peers_nearby": peers[:3],
            "cultural_restaurants": restaurants[:3],
            "community_events": events[:3],
            "resources": resources[:3],
            "subgraph": self._build_subgraph(
                mentors=mentors,
                peers=peers[:3],
                restaurants=restaurants[:3],
                events=events[:3],
            ),
        }

    def persist_profile_match(
        self, *, session_id: str, payload: ProfileInput, result: dict[str, Any]
    ) -> None:
        if not self.enabled:
            return

        try:
            self._write_query(
                UPSERT_SESSION_QUERY,
                {
                    "session_id": session_id,
                    "country_of_origin": payload.country_of_origin,
                    "home_city": payload.home_city,
                    "target_university": payload.target_university,
                    "target_city": payload.target_city,
                    "needs": normalize_text_list(payload.needs),
                    "interests": normalize_text_list(payload.interests),
                },
            )

            self._link_session_rows(
                session_id=session_id,
                rows=result.get("mentors_top3", []),
                query=LINK_MENTORS_QUERY,
            )
            self._link_session_rows(
                session_id=session_id,
                rows=result.get("peers_nearby", []),
                query=LINK_PEERS_QUERY,
            )
            self._link_session_rows(
                session_id=session_id,
                rows=result.get("cultural_restaurants", []),
                query=LINK_RESTAURANTS_QUERY,
            )
            self._link_session_rows(
                session_id=session_id,
                rows=result.get("community_events", []),
                query=LINK_EVENTS_QUERY,
            )
            self._link_session_rows(
                session_id=session_id,
                rows=result.get("resources", []),
                query=LINK_RESOURCES_QUERY,
            )
        except Neo4jError as exc:
            logger.warning("Neo4j write failed while persisting profile match: %s", exc)
            return

    def persist_plan(self, *, session_id: str, plan: dict[str, Any]) -> None:
        if not self.enabled:
            return

        steps = plan.get("steps", [])
        normalized_steps = []
        if isinstance(steps, list):
            for index, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                normalized_steps.append(
                    {
                        "id": f"{session_id}:step:{index}",
                        "position": index,
                        "day_range": str(step.get("day_range", "")),
                        "action": str(step.get("action", "")),
                        "entities": [
                            str(item)
                            for item in step.get("entities", [])
                            if item is not None and str(item).strip()
                        ],
                        "dependency_reason": str(step.get("dependency_reason", "")),
                        "source_node_ids": [
                            str(item)
                            for item in step.get("source_node_ids", [])
                            if item is not None and str(item).strip()
                        ],
                    }
                )

        try:
            self._write_query(
                UPSERT_PLAN_QUERY,
                {
                    "session_id": session_id,
                    "plan_id": session_id,
                    "plan_title": str(plan.get("plan_title", "")),
                    "priority_contacts": [
                        str(item)
                        for item in plan.get("priority_contacts", [])
                        if item is not None and str(item).strip()
                    ],
                    "warnings": [
                        str(item)
                        for item in plan.get("warnings", [])
                        if item is not None and str(item).strip()
                    ],
                    "confidence": float(plan.get("confidence", 0.0)),
                },
            )
            self._write_query(CLEAR_PLAN_STEPS_QUERY, {"plan_id": session_id})
            if normalized_steps:
                self._write_query(
                    UPSERT_PLAN_STEPS_QUERY,
                    {
                        "plan_id": session_id,
                        "steps": normalized_steps,
                    },
                )
        except Neo4jError as exc:
            logger.warning("Neo4j write failed while persisting generated plan: %s", exc)
            return

    def persist_bridge(
        self,
        *,
        session_id: str,
        term: str,
        context: str,
        home_country: str,
        bridge: dict[str, Any],
    ) -> None:
        if not self.enabled:
            return

        bridge_id = f"{session_id}:bridge:{self._slug(term)}"
        try:
            self._write_query(
                UPSERT_BRIDGE_QUERY,
                {
                    "session_id": session_id,
                    "bridge_id": bridge_id,
                    "term": str(bridge.get("term", term)),
                    "context": context,
                    "home_country": home_country,
                    "plain_explanation": str(bridge.get("plain_explanation", "")),
                    "home_context_analogy": str(bridge.get("home_context_analogy", "")),
                    "common_mistakes": [
                        str(item)
                        for item in bridge.get("common_mistakes", [])
                        if item is not None and str(item).strip()
                    ],
                    "what_to_do_next": [
                        str(item)
                        for item in bridge.get("what_to_do_next", [])
                        if item is not None and str(item).strip()
                    ],
                },
            )
        except Neo4jError as exc:
            logger.warning("Neo4j write failed while persisting bridge explanation: %s", exc)
            return

    def _link_session_rows(self, *, session_id: str, rows: Any, query: str) -> None:
        if not isinstance(rows, list) or not rows:
            return
        normalized = [row for row in rows if isinstance(row, dict)]
        if not normalized:
            return
        self._write_query(query, {"session_id": session_id, "rows": normalized})

    @staticmethod
    def _slug(value: str) -> str:
        text = (value or "").strip().lower()
        if not text:
            return "na"
        safe_chars = []
        for char in text:
            if char.isalnum():
                safe_chars.append(char)
            elif char in {" ", "-", "_"}:
                safe_chars.append("-")
        collapsed = "".join(safe_chars).strip("-")
        while "--" in collapsed:
            collapsed = collapsed.replace("--", "-")
        return collapsed or "na"

    def _rank_mentors(self, params: dict[str, Any], need_count: int) -> list[dict[str, Any]]:
        rows = self._run_query(MENTOR_QUERY, params)
        if not rows:
            rows = self._run_query(MENTOR_FALLBACK_QUERY, params)

        scored = []
        for row in rows:
            score = mentor_score(
                shared_country=bool(row.get("shared_country")),
                shared_university=True,
                need_overlap_count=int(row.get("need_overlap_count", 0)),
                requested_need_count=need_count,
                trust_score=float(row.get("trust_score", 0.0)),
            )
            reasons = []
            if row.get("shared_country"):
                reasons.append("Shared country context")
            reasons.append("Alumni network alignment")
            if row.get("need_overlap_count", 0) > 0:
                reasons.append("Need fit coverage")
            scored.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "score": score,
                    "trust_score": float(row.get("trust_score", 0.0)),
                    "response_rate": float(row.get("response_rate", 0.0)),
                    "languages": row.get("languages") or [],
                    "match_reasons": reasons,
                }
            )

        scored.sort(key=lambda item: (-item["score"], item["name"]))
        return scored[:3]

    def _build_subgraph(
        self,
        *,
        mentors: list[dict[str, Any]],
        peers: list[dict[str, Any]],
        restaurants: list[dict[str, Any]],
        events: list[dict[str, Any]],
    ) -> GraphSubgraph:
        student_id = "student_session"
        nodes = [
            GraphNode(
                id=student_id,
                label="You",
                type="student",
                metadata={},
            )
        ]
        edges: list[GraphEdge] = []

        for mentor in mentors:
            nodes.append(
                GraphNode(
                    id=mentor["id"],
                    label=mentor["name"],
                    type="mentor",
                    metadata={"score": mentor["score"]},
                )
            )
            edges.append(GraphEdge(source=student_id, target=mentor["id"], label="mentor"))

        for peer in peers:
            nodes.append(
                GraphNode(
                    id=peer["id"],
                    label=peer["name"],
                    type="peer",
                    metadata={"neighborhood": peer.get("neighborhood")},
                )
            )
            edges.append(GraphEdge(source=student_id, target=peer["id"], label="peer"))

        for restaurant in restaurants:
            nodes.append(
                GraphNode(
                    id=restaurant["id"],
                    label=restaurant["name"],
                    type="restaurant",
                    metadata={"distance_km": restaurant.get("distance_km")},
                )
            )
            edges.append(
                GraphEdge(source=student_id, target=restaurant["id"], label="food match")
            )

        for event in events:
            nodes.append(
                GraphNode(
                    id=event["id"],
                    label=event["name"],
                    type="event",
                    metadata={"start_time": event.get("start_time")},
                )
            )
            edges.append(
                GraphEdge(source=student_id, target=event["id"], label="community event")
            )

        return GraphSubgraph(nodes=nodes, edges=edges)

    def _demo_profile_match(self, payload: ProfileInput) -> dict[str, Any]:
        mentors = [
            {
                "id": "mentor_priya_sharma",
                "name": "Priya Sharma",
                "score": 0.94,
                "trust_score": 0.95,
                "response_rate": 0.88,
                "languages": ["English", "Hindi"],
                "match_reasons": ["Shared country context", "Need fit coverage"],
            },
            {
                "id": "mentor_rahul_iyer",
                "name": "Rahul Iyer",
                "score": 0.9,
                "trust_score": 0.92,
                "response_rate": 0.84,
                "languages": ["English", "Tamil"],
                "match_reasons": ["Shared country context", "Alumni network alignment"],
            },
            {
                "id": "mentor_anjali_reddy",
                "name": "Anjali Reddy",
                "score": 0.88,
                "trust_score": 0.9,
                "response_rate": 0.91,
                "languages": ["English", "Telugu"],
                "match_reasons": ["Shared country context", "Need fit coverage"],
            },
        ]

        peers = [
            {"id": "peer_aisha_khan", "name": "Aisha Khan", "neighborhood": "Hyde Park"},
            {"id": "peer_vikram_patel", "name": "Vikram Patel", "neighborhood": "South Loop"},
            {"id": "peer_nandini_rao", "name": "Nandini Rao", "neighborhood": "Bridgeport"},
        ]

        restaurants = [
            {
                "id": "restaurant_dosa_house",
                "name": "Hema's Kitchen",
                "distance_km": 2.8,
                "price_level": 2,
            },
            {
                "id": "restaurant_sangam_chettinad",
                "name": "Udupi Palace",
                "distance_km": 3.4,
                "price_level": 2,
            },
            {
                "id": "restaurant_madras_pavilion",
                "name": "Ghareeb Nawaz",
                "distance_km": 4.1,
                "price_level": 1,
            },
        ]

        events = [
            {
                "id": "event_international_orientation",
                "name": "International Student Orientation Mixer",
                "start_time": "2026-08-21T17:30:00-05:00",
                "location": "Ida Noyes Hall",
                "category": "orientation",
            },
            {
                "id": "event_indian_grad_welcome",
                "name": "Indian Graduate Welcome Circle",
                "start_time": "2026-08-24T18:00:00-05:00",
                "location": "Reynolds Club",
                "category": "community",
            },
            {
                "id": "event_bank_onboarding_session",
                "name": "Newcomer Banking Setup Session",
                "start_time": "2026-08-28T13:00:00-05:00",
                "location": "Harper Memorial Library",
                "category": "banking",
            },
        ]

        resources = [
            {
                "id": "resource_bank_doc_checklist",
                "name": "Bank Account Documentation Checklist",
                "type": "checklist",
                "url": "https://example.org/bank-checklist",
            },
            {
                "id": "resource_housing_office",
                "name": "UChicago Housing & Residence Life",
                "type": "office",
                "url": "https://housing.uchicago.edu/",
            },
            {
                "id": "resource_uchicago_international_office",
                "name": "UChicago Office of International Affairs",
                "type": "office",
                "url": "https://internationalaffairs.uchicago.edu",
            },
        ]

        return {
            "mentors_top3": mentors,
            "peers_nearby": peers,
            "cultural_restaurants": restaurants,
            "community_events": events,
            "resources": resources,
            "subgraph": self._build_subgraph(
                mentors=mentors, peers=peers, restaurants=restaurants, events=events
            ),
            "demo_mode": not self.enabled,
            "echo_profile": {
                "country_of_origin": payload.country_of_origin,
                "target_university": payload.target_university,
            },
        }
