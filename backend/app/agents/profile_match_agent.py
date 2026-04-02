"""Profile + graph match: Neo4j evidence, deterministic mentor ranking, subgraph for UI."""

from __future__ import annotations

import uuid
from typing import Any

from app.db.neo4j_client import Neo4jClient
from app.models.schemas import (
    EventCard,
    GraphEdge,
    GraphNode,
    MentorCard,
    PeerCard,
    ProfileMatchRequest,
    ProfileMatchResponse,
    ResourceCard,
    RestaurantCard,
    Subgraph,
)


def _country_code_hint(country_name: str) -> str:
    n = country_name.strip().lower()
    if n in ("india", "in"):
        return "IN"
    if n in ("united states", "usa", "us"):
        return "US"
    return ""


def _mentor_score(
    *,
    shared_country: bool,
    shared_uni: bool,
    need_overlap: float,
    trust_score: float,
) -> float:
    return (
        0.30 * (1.0 if shared_country else 0.0)
        + 0.25 * (1.0 if shared_uni else 0.0)
        + 0.25 * need_overlap
        + 0.20 * trust_score
    )


def _topological_tasks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order tasks using PRECEDES edges (Kahn-style)."""
    from collections import defaultdict

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[tuple[str, str]] = []
    for row in rows:
        tid = row["tid"]
        nodes[tid] = {
            "id": tid,
            "name": row["name"],
            "priority": row.get("priority", 0),
            "estimated_day_window": row.get("estimated_day_window", ""),
        }
        nxt = row.get("next_id")
        if nxt:
            edges.append((tid, nxt))

    adj: defaultdict[str, list[str]] = defaultdict(list)
    incoming: dict[str, int] = {tid: 0 for tid in nodes}
    for a, b in edges:
        adj[a].append(b)
        incoming[b] += 1
    queue = [tid for tid in nodes if incoming[tid] == 0]
    order: list[dict[str, Any]] = []
    while queue:
        tid = queue.pop(0)
        order.append(nodes[tid])
        for b in adj[tid]:
            incoming[b] -= 1
            if incoming[b] == 0:
                queue.append(b)
    seen = {x["id"] for x in order}
    for tid, node in nodes.items():
        if tid not in seen:
            order.append(node)
    return order


async def run_profile_match(
    neo4j: Neo4jClient,
    profile: ProfileMatchRequest,
) -> ProfileMatchResponse:
    session_id = str(uuid.uuid4())
    country = profile.country_of_origin.strip()
    country_code = _country_code_hint(country)
    uni = profile.target_university.strip()
    city = profile.target_city.strip()
    needs = [n.strip().lower() for n in profile.needs if n.strip()]

    mentor_rows = await neo4j.query(
        """
        MATCH (m:Mentor)-[:FROM_COUNTRY]->(c:Country)
        WHERE c.name = $country OR ($country_code <> '' AND c.code = $country_code)
        MATCH (m)-[:ALUM_OF]->(u:University {name: $uni})
        OPTIONAL MATCH (m)-[:CAN_HELP_WITH]->(n:Need)
        RETURN m.id AS id, m.name AS name, m.trust_score AS trust_score,
               m.languages AS languages,
               coalesce(m.email, '') AS email,
               coalesce(m.linkedin_url, '') AS linkedin_url,
               coalesce(m.connect_hint, '') AS connect_hint,
               collect(DISTINCT n.name) AS covered
        """,
        {
            "country": country,
            "country_code": country_code,
            "uni": uni,
        },
    )

    ranked: list[tuple[float, dict[str, Any]]] = []
    for row in mentor_rows:
        covered = [c for c in (row.get("covered") or []) if c]
        overlap = len(set(covered) & set(needs)) / max(len(needs), 1) if needs else 0.5
        trust = float(row.get("trust_score") or 0.0)
        score = _mentor_score(
            shared_country=True,
            shared_uni=True,
            need_overlap=overlap,
            trust_score=trust,
        )
        reasons = [
            "Shared home country context",
            f"Alumni of {uni}",
            f"Need overlap on: {', '.join(covered) or 'general support'}",
            f"Trust score {trust:.2f}",
        ]
        ranked.append(
            (
                score,
                {
                    "id": row["id"],
                    "name": row["name"],
                    "trust_score": trust,
                    "languages": list(row.get("languages") or []),
                    "match_score": round(score, 4),
                    "match_reasons": reasons,
                    "email": str(row.get("email") or ""),
                    "linkedin_url": str(row.get("linkedin_url") or ""),
                    "connect_hint": str(row.get("connect_hint") or ""),
                },
            )
        )
    ranked.sort(key=lambda x: x[0], reverse=True)
    mentors_top3: list[MentorCard] = []
    for _, m in ranked[:3]:
        reasons = m["match_reasons"]
        why = " · ".join(reasons[:2]) if len(reasons) >= 2 else (reasons[0] if reasons else "Graph match")
        mentors_top3.append(
            MentorCard(
                id=m["id"],
                name=m["name"],
                trust_score=m["trust_score"],
                languages=m["languages"],
                match_score=m["match_score"],
                match_reasons=m["match_reasons"],
                why_this_match=why,
                confidence_score=float(m["match_score"]),
                email=m.get("email") or "",
                linkedin_url=m.get("linkedin_url") or "",
                connect_hint=m.get("connect_hint") or "",
            )
        )

    peer_rows = await neo4j.query(
        """
        MATCH (p:Peer)-[:STUDIES_AT]->(u:University {name: $uni})
        RETURN p.id AS id, p.name AS name, p.university AS university, p.neighborhood AS neighborhood,
               coalesce(p.email, '') AS email, coalesce(p.connect_hint, '') AS connect_hint
        LIMIT 8
        """,
        {"uni": uni},
    )
    peers_nearby = [
        PeerCard(
            id=r["id"],
            name=r["name"],
            university=r["university"],
            neighborhood=r["neighborhood"],
            email=str(r.get("email") or ""),
            connect_hint=str(r.get("connect_hint") or ""),
        )
        for r in peer_rows
    ]

    restaurant_rows = await neo4j.query(
        """
        MATCH (r:Restaurant)-[:SERVES_CUISINE]->(c:Country)
        WHERE c.name = $country OR ($country_code <> '' AND c.code = $country_code)
        RETURN r.id AS id, r.name AS name, r.price_level AS price_level, r.distance_km AS distance_km
        LIMIT 8
        """,
        {"country": country, "country_code": country_code},
    )
    cultural_restaurants = [
        RestaurantCard(
            id=r["id"],
            name=r["name"],
            price_level=int(r.get("price_level") or 0),
            distance_km=float(r.get("distance_km") or 0.0),
        )
        for r in restaurant_rows
    ]

    event_rows = await neo4j.query(
        """
        MATCH (e:Event)-[:RELEVANT_TO]->(c:Country)
        WHERE c.name = $country OR ($country_code <> '' AND c.code = $country_code)
        MATCH (e)-[:OCCURS_IN]->(city:City)
        WHERE city.name = $city
        RETURN e.id AS id, e.name AS name, e.start_time AS start_time, e.location AS location, e.category AS category
        LIMIT 8
        """,
        {"country": country, "country_code": country_code, "city": city},
    )
    community_events = [
        EventCard(
            id=r["id"],
            name=r["name"],
            start_time=str(r.get("start_time") or ""),
            location=str(r.get("location") or ""),
            category=str(r.get("category") or ""),
        )
        for r in event_rows
    ]

    resource_rows = await neo4j.query(
        """
        MATCH (res:Resource)-[:HELPS_WITH]->(n:Need)
        WHERE n.name IN $needs
        RETURN DISTINCT res.id AS id, res.name AS name, res.resource_type AS resource_type
        LIMIT 12
        """,
        {"needs": needs},
    )
    resources = [
        ResourceCard(
            id=r["id"],
            name=r["name"],
            resource_type=str(r.get("resource_type") or ""),
        )
        for r in resource_rows
    ]

    task_rows = await neo4j.query(
        """
        MATCH (t:Task)
        OPTIONAL MATCH (t)-[:PRECEDES]->(nxt:Task)
        WITH t, head(collect(nxt.id)) AS next_id
        RETURN t.id AS tid, t.name AS name, t.priority AS priority, t.estimated_day_window AS estimated_day_window,
               next_id AS next_id
        """,
        {},
    )
    tasks_ordered = _topological_tasks([dict(r) for r in task_rows])

    student_profile = {
        "country_of_origin": country,
        "home_city": profile.home_city,
        "target_university": uni,
        "target_city": city,
        "needs": needs,
        "interests": profile.interests,
    }

    evidence_bundle: dict[str, Any] = {
        "mentors": [m.model_dump() for m in mentors_top3],
        "peers": [p.model_dump() for p in peers_nearby],
        "restaurants": [r.model_dump() for r in cultural_restaurants],
        "events": [e.model_dump() for e in community_events],
        "resources": [r.model_dump() for r in resources],
        "tasks_ordered": tasks_ordered,
        "student_profile": student_profile,
    }

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    eid = 0

    student_node_id = f"student_{session_id}"

    def add_node(nid: str, label: str, group: str, subtitle: str | None = None) -> None:
        if not any(x.id == nid for x in nodes):
            nodes.append(GraphNode(id=nid, label=label, group=group, subtitle=subtitle))

    add_node(
        student_node_id,
        f"You · {profile.home_city.strip()}",
        "student",
        f"{country} → {uni}",
    )

    for m in mentors_top3:
        add_node(m.id, m.name, "mentor", f"score {m.match_score:.2f}")
    for p in peers_nearby:
        add_node(p.id, p.name, "peer", p.neighborhood)
    for r in cultural_restaurants:
        add_node(r.id, r.name, "restaurant", f"{r.distance_km} km")
    for e in community_events:
        add_node(e.id, e.name, "event", e.category)
    for res in resources:
        add_node(res.id, res.name, "resource", res.resource_type)
    for t in tasks_ordered:
        add_node(t["id"], str(t["name"]), "task", str(t.get("estimated_day_window", "")))

    seen_e: set[tuple[str, str]] = set()

    def add_edge(from_id: str, to_id: str, prefix: str) -> None:
        nonlocal eid
        key = (from_id, to_id)
        if key in seen_e:
            return
        seen_e.add(key)
        eid += 1
        edges.append(GraphEdge(id=f"{prefix}_{eid}", from_=from_id, to=to_id))

    # Hub-and-spoke from the session student to all evidence entities (not just the top mentor).
    for m in mentors_top3:
        add_edge(student_node_id, m.id, "sm")
    for p in peers_nearby[:8]:
        add_edge(student_node_id, p.id, "sp")
    for r in cultural_restaurants:
        add_edge(student_node_id, r.id, "sr")
    for ev in community_events:
        add_edge(student_node_id, ev.id, "sev")
    for res in resources:
        add_edge(student_node_id, res.id, "sres")

    # Ordered task chain from Neo4j evidence (dependency story).
    for i in range(len(tasks_ordered) - 1):
        add_edge(tasks_ordered[i]["id"], tasks_ordered[i + 1]["id"], "task")

    subgraph = Subgraph(nodes=nodes, edges=edges)

    nc = max(len(needs), 1)
    res_score = min(1.0, len(resources) / max(nc * 2, 1))
    mentor_cov = min(1.0, len(mentors_top3) / 3) if mentors_top3 else 0.0
    support_coverage_score = round(0.55 * res_score + 0.45 * mentor_cov, 3)

    peer_p = min(1.0, len(peers_nearby) / 5)
    event_p = min(1.0, len(community_events) / 5)
    food_p = min(1.0, len(cultural_restaurants) / 5)
    belonging_score = round(0.28 * peer_p + 0.24 * event_p + 0.24 * food_p + 0.24 * mentor_cov, 3)

    return ProfileMatchResponse(
        session_id=session_id,
        mentors_top3=mentors_top3,
        peers_nearby=peers_nearby,
        cultural_restaurants=cultural_restaurants,
        community_events=community_events,
        resources=resources,
        evidence_bundle=evidence_bundle,
        subgraph=subgraph,
        support_coverage_score=support_coverage_score,
        belonging_score=belonging_score,
    )
