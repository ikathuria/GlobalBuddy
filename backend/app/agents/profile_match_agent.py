"""Profile + graph match: Neo4j evidence, deterministic mentor ranking, subgraph for UI."""

from __future__ import annotations

import re
import uuid
from typing import Any
from urllib.parse import quote_plus

from app.db.neo4j_client import Neo4jClient
from app.models.schemas import (
    EventCard,
    GraphEdge,
    GraphNode,
    LocalPlaceCard,
    MentorCard,
    PeerCard,
    ProfileMatchRequest,
    ProfileMatchResponse,
    ResourceCard,
    RestaurantCard,
    Subgraph,
    TransitTipCard,
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


def _profile_tokens(profile: ProfileMatchRequest) -> set[str]:
    raw: list[str] = [
        profile.country_of_origin,
        profile.religion_or_observance,
        profile.diet,
        profile.cultural_background,
        *profile.interests,
    ]
    tokens: set[str] = set()
    for text in raw:
        for part in re.split(r"[\s,;/|]+", str(text).lower().strip()):
            if len(part) >= 2:
                tokens.add(part)
    uni = profile.target_university.lower()
    if "illinois institute" in uni or uni.strip() == "iit" or " iit" in uni or uni.startswith("iit "):
        tokens.update({"near_iit", "iit"})
    expanded: set[str] = set()
    for t in tokens:
        expanded.add(t)
        if t in ("hindu", "mandir"):
            expanded.update({"hindu", "south_asian", "indian"})
        if t in ("muslim", "islam", "mosque"):
            expanded.update({"muslim", "south_asian"})
        if t in ("sikh", "gurdwara", "punjabi"):
            expanded.update({"sikh", "punjabi", "south_asian"})
        if t in ("christian", "church", "catholic"):
            expanded.update({"christian"})
        if t in ("veg", "vegetarian", "vegan"):
            expanded.update({"vegetarian", "veg"})
        if t == "halal":
            expanded.update({"halal", "halal_section_typical"})
    return expanded


def _tags_match_score(tags: list[Any] | None, tokens: set[str]) -> float:
    if not tags:
        return 0.0
    hits = 0
    for tag in tags:
        tl = str(tag).lower().replace("_", " ")
        raw_tag = str(tag).lower()
        for tok in tokens:
            if len(tok) < 2:
                continue
            if tok in tl or tl.startswith(tok) or tok.replace(" ", "_") in raw_tag:
                hits += 1
                break
    return hits / len(tags)


def _why_from_tags(tags: list[Any] | None, score: float, fallback: str) -> str:
    if score <= 0 or not tags:
        return fallback
    shown = ", ".join(str(x) for x in tags[:4])
    return f"Graph tags ({shown}) overlap your profile — confirm hours and access before visiting."


def _maps_url(row: dict[str, Any]) -> str:
    link = str(row.get("maps_link") or "").strip()
    if link:
        return link
    q = str(row.get("maps_query") or row.get("name") or "").strip()
    if not q:
        return ""
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(q)}"


def _row_to_local_place(
    row: dict[str, Any],
    place_kind: str,
    why: str,
) -> LocalPlaceCard:
    lat, lon = row.get("latitude"), row.get("longitude")
    return LocalPlaceCard(
        id=str(row["id"]),
        name=str(row.get("name") or ""),
        place_kind=place_kind,
        subtype=str(row.get("subtype") or ""),
        address=str(row.get("address") or ""),
        neighborhood=str(row.get("neighborhood") or ""),
        latitude=float(lat) if lat is not None else None,
        longitude=float(lon) if lon is not None else None,
        maps_query=str(row.get("maps_query") or ""),
        maps_link=_maps_url(row),
        why_recommended=why,
    )


def _row_to_transit(row: dict[str, Any]) -> TransitTipCard:
    return TransitTipCard(
        id=str(row["id"]),
        name=str(row["name"]),
        summary=str(row.get("summary") or ""),
        route_hint=str(row.get("route_hint") or ""),
        neighborhood=str(row.get("neighborhood") or ""),
        maps_link=_maps_url(row),
    )


def _transit_rank_score(row: dict[str, Any], tokens: set[str]) -> float:
    blob = f"{row.get('name', '')} {row.get('route_hint', '')} {row.get('summary', '')}".lower()
    base = 0.25
    if "iit" in tokens and "iit" in blob:
        base += 0.45
    if "green" in blob and ("line" in blob or "cta" in blob):
        base += 0.15
    return min(1.0, base)


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
    profile_tok = _profile_tokens(profile)

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
        RETURN e.id AS id, e.name AS name, e.start_time AS start_time, e.location AS location, e.category AS category,
               coalesce(e.notes, '') AS notes, coalesce(e.maps_query, '') AS maps_query, coalesce(e.maps_link, '') AS maps_link
        LIMIT 12
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
            notes=str(r.get("notes") or ""),
            maps_query=str(r.get("maps_query") or ""),
            maps_link=_maps_url(dict(r)),
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

    worship_rows = await neo4j.query(
        """
        MATCH (pw:PlaceOfWorship)
        WHERE pw.city_name = $city
        OPTIONAL MATCH (pw)-[:RELEVANT_TO]->(c:Country)
        WITH pw, collect(DISTINCT c.name) AS countries
        RETURN pw.id AS id, pw.name AS name, pw.subtype AS subtype, pw.address AS address,
               pw.neighborhood AS neighborhood, pw.latitude AS latitude, pw.longitude AS longitude,
               pw.maps_query AS maps_query, pw.maps_link AS maps_link,
               pw.audience_tags AS audience_tags, countries AS relevant_countries
        """,
        {"city": city},
    )
    scored_worship: list[tuple[float, dict[str, Any]]] = []
    for row in worship_rows:
        tags = list(row.get("audience_tags") or [])
        tag_s = _tags_match_score(tags, profile_tok)
        countries = [str(c) for c in (row.get("relevant_countries") or []) if c]
        country_boost = 0.22 if country in countries else 0.0
        raw = min(1.0, 0.12 + tag_s * 0.72 + country_boost)
        scored_worship.append((raw, dict(row)))
    scored_worship.sort(key=lambda x: (-x[0], str(x[1].get("name") or "")))

    grocery_rows = await neo4j.query(
        """
        MATCH (gs:GroceryStore)
        WHERE gs.city_name = $city
        OPTIONAL MATCH (gs)-[:RELEVANT_TO]->(c:Country)
        WITH gs, collect(DISTINCT c.name) AS countries
        RETURN gs.id AS id, gs.name AS name, gs.address AS address, gs.neighborhood AS neighborhood,
               gs.latitude AS latitude, gs.longitude AS longitude, gs.maps_query AS maps_query, gs.maps_link AS maps_link,
               gs.diet_tags AS diet_tags, countries AS relevant_countries
        """,
        {"city": city},
    )
    scored_grocery: list[tuple[float, dict[str, Any]]] = []
    for row in grocery_rows:
        tags = list(row.get("diet_tags") or [])
        tag_s = _tags_match_score(tags, profile_tok)
        countries = [str(c) for c in (row.get("relevant_countries") or []) if c]
        country_boost = 0.2 if country in countries else 0.0
        raw = min(1.0, 0.1 + tag_s * 0.75 + country_boost)
        scored_grocery.append((raw, dict(row)))
    scored_grocery.sort(key=lambda x: (-x[0], str(x[1].get("name") or "")))

    housing_rows = await neo4j.query(
        """
        MATCH (h:HousingArea)-[:NEAR_UNIVERSITY]->(u:University {name: $uni})
        WHERE h.city_name = $city
        RETURN h.id AS id, h.name AS name, h.address AS address, h.neighborhood AS neighborhood,
               h.latitude AS latitude, h.longitude AS longitude, h.maps_query AS maps_query, h.maps_link AS maps_link,
               h.audience_tags AS audience_tags
        """,
        {"city": city, "uni": uni},
    )
    scored_housing: list[tuple[float, dict[str, Any]]] = []
    for row in housing_rows:
        tags = list(row.get("audience_tags") or [])
        tag_s = _tags_match_score(tags, profile_tok)
        raw = min(1.0, 0.18 + tag_s * 0.62 + (0.2 if "housing" in needs else 0.0))
        scored_housing.append((raw, dict(row)))
    scored_housing.sort(key=lambda x: (-x[0], str(x[1].get("name") or "")))

    exploration_rows = await neo4j.query(
        """
        MATCH (ex:ExplorationSpot)-[:LOCATED_IN]->(ct:City)
        WHERE ct.name = $city
        RETURN ex.id AS id, ex.name AS name, ex.subtype AS subtype, ex.address AS address, ex.neighborhood AS neighborhood,
               ex.latitude AS latitude, ex.longitude AS longitude, ex.maps_query AS maps_query, ex.maps_link AS maps_link,
               ex.audience_tags AS audience_tags
        """,
        {"city": city},
    )
    scored_explore: list[tuple[float, dict[str, Any]]] = []
    for row in exploration_rows:
        tags = list(row.get("audience_tags") or [])
        tag_s = _tags_match_score(tags, profile_tok)
        raw = min(1.0, 0.15 + tag_s * 0.8)
        scored_explore.append((raw, dict(row)))
    scored_explore.sort(key=lambda x: (-x[0], str(x[1].get("name") or "")))

    transit_rows = await neo4j.query(
        """
        MATCH (tt:TransitTip)-[:GOOD_FOR]->(ct:City)
        WHERE ct.name = $city AND tt.city_name = $city
        RETURN tt.id AS id, tt.name AS name, tt.summary AS summary, tt.route_hint AS route_hint,
               tt.neighborhood AS neighborhood, tt.maps_link AS maps_link, coalesce(tt.maps_query, '') AS maps_query
        """,
        {"city": city},
    )
    scored_transit: list[tuple[float, dict[str, Any]]] = []
    for row in transit_rows:
        r = dict(row)
        scored_transit.append((_transit_rank_score(r, profile_tok), r))
    scored_transit.sort(key=lambda x: (-x[0], str(x[1].get("name") or "")))

    fb_worship = "In graph for Chicago — align with your community needs in Neo4j."
    places_of_worship = [
        _row_to_local_place(
            row,
            "worship",
            _why_from_tags(list(row.get("audience_tags") or []), _tags_match_score(row.get("audience_tags"), profile_tok), fb_worship),
        )
        for _, row in scored_worship[:6]
    ]
    fb_grocery = "Listed in graph for essentials — verify product availability in store."
    grocery_stores = [
        _row_to_local_place(
            row,
            "grocery",
            _why_from_tags(list(row.get("diet_tags") or []), _tags_match_score(row.get("diet_tags"), profile_tok), fb_grocery),
        )
        for _, row in scored_grocery[:6]
    ]
    fb_housing = "Near your target university in the graph — tour and verify leases independently."
    housing_areas = [
        _row_to_local_place(
            row,
            "housing",
            _why_from_tags(list(row.get("audience_tags") or []), _tags_match_score(row.get("audience_tags"), profile_tok), fb_housing),
        )
        for _, row in scored_housing[:6]
    ]
    fb_exp = "Downtown / exploration node from graph — check hours before visiting."
    exploration_spots = [
        _row_to_local_place(
            row,
            "exploration",
            _why_from_tags(list(row.get("audience_tags") or []), _tags_match_score(row.get("audience_tags"), profile_tok), fb_exp),
        )
        for _, row in scored_explore[:6]
    ]
    transit_tips = [_row_to_transit(row) for _, row in scored_transit[:6]]

    fit_samples: list[float] = []
    if scored_worship:
        fit_samples.append(scored_worship[0][0])
    if scored_grocery:
        fit_samples.append(scored_grocery[0][0])
    if scored_explore:
        fit_samples.append(scored_explore[0][0])
    cultural_fit_score = round(sum(fit_samples) / len(fit_samples), 3) if fit_samples else 0.0

    best_weekend_outing = ""
    if scored_explore:
        top = scored_explore[0][1]
        best_weekend_outing = (
            f"Graph pick: {top.get('name')} — directions via Maps link in bundle; confirm hours independently."
        )
    elif community_events:
        best_weekend_outing = (
            f"Graph event to research: {community_events[0].name} — see notes field for disclaimers; verify with organizers."
        )

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
        "cultural_background": profile.cultural_background,
        "religion_or_observance": profile.religion_or_observance,
        "diet": profile.diet,
    }

    evidence_bundle: dict[str, Any] = {
        "mentors": [m.model_dump() for m in mentors_top3],
        "peers": [p.model_dump() for p in peers_nearby],
        "restaurants": [r.model_dump() for r in cultural_restaurants],
        "events": [e.model_dump() for e in community_events],
        "resources": [r.model_dump() for r in resources],
        "tasks_ordered": tasks_ordered,
        "student_profile": student_profile,
        "places_of_worship": [p.model_dump() for p in places_of_worship],
        "grocery_stores": [p.model_dump() for p in grocery_stores],
        "housing_areas": [p.model_dump() for p in housing_areas],
        "exploration_spots": [p.model_dump() for p in exploration_spots],
        "transit_tips": [t.model_dump() for t in transit_tips],
    }

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    eid = 0

    student_node_id = f"student_{session_id}"

    def add_node(
        nid: str,
        label: str,
        group: str,
        subtitle: str | None = None,
        *,
        address: str | None = None,
        maps_query: str | None = None,
        maps_link: str | None = None,
        why_recommended: str | None = None,
    ) -> None:
        if not any(x.id == nid for x in nodes):
            nodes.append(
                GraphNode(
                    id=nid,
                    label=label,
                    group=group,
                    subtitle=subtitle,
                    address=address,
                    maps_query=maps_query or None,
                    maps_link=maps_link or None,
                    why_recommended=why_recommended,
                )
            )

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
        add_node(
            e.id,
            e.name,
            "event",
            e.category,
            maps_query=e.maps_query or None,
            maps_link=e.maps_link or None,
            why_recommended=(e.notes[:200] + "…") if len(e.notes) > 200 else (e.notes or None),
        )
    for res in resources:
        add_node(res.id, res.name, "resource", res.resource_type)
    for t in tasks_ordered:
        add_node(t["id"], str(t["name"]), "task", str(t.get("estimated_day_window", "")))

    for p in places_of_worship:
        add_node(
            p.id,
            p.name,
            "place_worship",
            p.neighborhood or p.subtype,
            address=p.address or None,
            maps_query=p.maps_query or None,
            maps_link=p.maps_link or None,
            why_recommended=p.why_recommended or None,
        )
    for p in grocery_stores:
        add_node(
            p.id,
            p.name,
            "grocery",
            p.neighborhood,
            address=p.address or None,
            maps_query=p.maps_query or None,
            maps_link=p.maps_link or None,
            why_recommended=p.why_recommended or None,
        )
    for p in housing_areas:
        add_node(
            p.id,
            p.name,
            "housing_area",
            p.neighborhood,
            address=p.address or None,
            maps_query=p.maps_query or None,
            maps_link=p.maps_link or None,
            why_recommended=p.why_recommended or None,
        )
    for p in exploration_spots:
        add_node(
            p.id,
            p.name,
            "exploration",
            p.subtype or p.neighborhood,
            address=p.address or None,
            maps_query=p.maps_query or None,
            maps_link=p.maps_link or None,
            why_recommended=p.why_recommended or None,
        )
    for tt in transit_tips:
        add_node(
            tt.id,
            tt.name,
            "transit_tip",
            tt.neighborhood or "Transit",
            address=None,
            maps_query=None,
            maps_link=tt.maps_link or None,
            why_recommended=(tt.summary[:160] + "…") if len(tt.summary) > 160 else (tt.summary or None),
        )

    seen_e: set[tuple[str, str]] = set()

    def add_edge(from_id: str, to_id: str, prefix: str) -> None:
        nonlocal eid
        key = (from_id, to_id)
        if key in seen_e:
            return
        seen_e.add(key)
        eid += 1
        edges.append(GraphEdge(id=f"{prefix}_{eid}", from_=from_id, to=to_id))

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
    for p in places_of_worship:
        add_edge(student_node_id, p.id, "sw")
    for p in grocery_stores:
        add_edge(student_node_id, p.id, "sg")
    for p in housing_areas:
        add_edge(student_node_id, p.id, "sh")
    for p in exploration_spots:
        add_edge(student_node_id, p.id, "sx")
    for tt in transit_tips:
        add_edge(student_node_id, tt.id, "stt")

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
    local_n = len(places_of_worship) + len(grocery_stores) + len(exploration_spots) + len(transit_tips) + len(housing_areas)
    local_p = min(1.0, local_n / 14)
    belonging_score = round(
        0.20 * peer_p + 0.16 * event_p + 0.16 * food_p + 0.20 * mentor_cov + 0.14 * local_p + 0.14 * cultural_fit_score,
        3,
    )

    return ProfileMatchResponse(
        session_id=session_id,
        mentors_top3=mentors_top3,
        peers_nearby=peers_nearby,
        cultural_restaurants=cultural_restaurants,
        community_events=community_events,
        resources=resources,
        places_of_worship=places_of_worship,
        grocery_stores=grocery_stores,
        housing_areas=housing_areas,
        exploration_spots=exploration_spots,
        transit_tips=transit_tips,
        evidence_bundle=evidence_bundle,
        subgraph=subgraph,
        support_coverage_score=support_coverage_score,
        belonging_score=belonging_score,
        cultural_fit_score=cultural_fit_score,
        best_weekend_outing=best_weekend_outing,
    )
