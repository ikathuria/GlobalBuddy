"""Markdown-backed graph adapter for public Globalदोस्त knowledge."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any
from urllib.parse import quote_plus

import yaml

from app.models.schemas import (
    CommunityGroupCard,
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
from app.utils.stages import infer_user_stage


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
REQUIRED_TYPES = {
    "Mentor",
    "Peer",
    "University",
    "Task",
    "LocalEntity",
    "Event",
    "CommunityGroup",
    "Guide",
}
LOCAL_PLACE_TYPES = {"PlaceOfWorship", "GroceryStore", "HousingArea", "ExplorationSpot"}
STAGE_CATEGORY_WEIGHTS = {
    "newcomer": {
        "mentor": 1.18,
        "resource": 1.14,
        "task": 1.12,
        "peer": 0.92,
        "event": 0.94,
        "community_group": 0.98,
        "local": 1.0,
    },
    "settler": {
        "mentor": 1.02,
        "resource": 0.98,
        "task": 0.96,
        "peer": 1.18,
        "event": 1.12,
        "community_group": 1.18,
        "local": 1.04,
    },
    "local": {
        "mentor": 0.94,
        "resource": 0.9,
        "task": 0.88,
        "peer": 1.06,
        "event": 1.2,
        "community_group": 1.18,
        "local": 1.18,
    },
    "mentor": {
        "mentor": 0.86,
        "resource": 0.86,
        "task": 0.84,
        "peer": 1.04,
        "event": 1.18,
        "community_group": 1.22,
        "local": 1.2,
    },
}


def _stage_weight(stage: str, category: str) -> float:
    return STAGE_CATEGORY_WEIGHTS.get(stage, STAGE_CATEGORY_WEIGHTS["newcomer"]).get(category, 1.0)


@dataclass(frozen=True)
class MarkdownNode:
    id: str
    type: str
    title: str
    city: str
    data: dict[str, Any]
    body: str
    path: Path
    wikilinks: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MarkdownEdge:
    id: str
    from_id: str
    to_id: str
    kind: str


@dataclass
class GraphValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    if isinstance(value, str):
        return [value]
    return [value]


def _as_str_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _as_list(value) if str(item).strip()]


def _lower_set(value: Any) -> set[str]:
    return {item.lower() for item in _as_str_list(value)}


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")


def _text_matches(needle: str, candidates: Any) -> bool:
    n = str(needle or "").strip().lower()
    if not n:
        return False
    for candidate in _as_str_list(candidates):
        c = candidate.lower()
        if n == c or n in c or c in n:
            return True
    return False


def _country_code_hint(country_name: str) -> str:
    n = country_name.strip().lower()
    if n in {"india", "in"}:
        return "IN"
    if n in {"united states", "usa", "us"}:
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
        for part in re.split(r"[\s,;/|_]+", str(text).lower().strip()):
            if len(part) >= 2:
                tokens.add(part)

    uni = profile.target_university.lower()
    if "illinois institute" in uni or uni.strip() == "iit" or " iit" in uni or uni.startswith("iit "):
        tokens.update({"near_iit", "iit"})

    expanded: set[str] = set()
    for token in tokens:
        expanded.add(token)
        if token in {"hindu", "mandir"}:
            expanded.update({"hindu", "south_asian", "indian"})
        if token in {"muslim", "islam", "mosque"}:
            expanded.update({"muslim", "south_asian"})
        if token in {"sikh", "gurdwara", "punjabi"}:
            expanded.update({"sikh", "punjabi", "south_asian"})
        if token in {"veg", "vegetarian", "vegan"}:
            expanded.update({"vegetarian", "veg"})
        if token == "halal":
            expanded.update({"halal", "halal_section_typical"})
    return expanded


def _tags_match_score(tags: Any, tokens: set[str]) -> float:
    tag_list = _as_str_list(tags)
    if not tag_list:
        return 0.0
    hits = 0
    for tag in tag_list:
        tl = tag.lower().replace("_", " ")
        raw_tag = tag.lower()
        for tok in tokens:
            if len(tok) < 2:
                continue
            if tok in tl or tl.startswith(tok) or tok.replace(" ", "_") in raw_tag:
                hits += 1
                break
    return hits / len(tag_list)


def _why_from_tags(tags: Any, score: float, fallback: str) -> str:
    tag_list = _as_str_list(tags)
    if score <= 0 or not tag_list:
        return fallback
    shown = ", ".join(tag_list[:4])
    return f"Graph tags ({shown}) overlap your profile; confirm hours and access before visiting."


def _maps_url(data: dict[str, Any]) -> str:
    link = str(data.get("maps_link") or "").strip()
    if link:
        return link
    q = str(data.get("maps_query") or data.get("title") or data.get("name") or "").strip()
    if not q:
        return ""
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(q)}"


class MarkdownGraphService:
    source = "markdown"

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()
        self.nodes: dict[str, MarkdownNode] = {}
        self.edges: list[MarkdownEdge] = []
        self.validation = GraphValidationReport()
        self.reload()

    def reload(self) -> None:
        parsed, duplicates = self._parse_nodes()
        self.nodes = parsed
        self.edges = self._build_edges()
        self.validation = self._validate(duplicates)

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok" if self.validation.ok else "error",
            "source": self.source,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "validation_errors": self.validation.errors,
            "validation_warnings": self.validation.warnings,
        }

    def nodes_by_type(self, node_type: str, city: str | None = None) -> list[MarkdownNode]:
        return [
            node
            for node in self.nodes.values()
            if node.type == node_type and (not city or not node.city or node.city.lower() == city.lower())
        ]

    def profile_match(self, profile: ProfileMatchRequest) -> ProfileMatchResponse:
        import uuid

        session_id = str(uuid.uuid4())
        country = profile.country_of_origin.strip()
        country_code = _country_code_hint(country)
        uni = profile.target_university.strip()
        city = profile.target_city.strip()
        needs = [n.strip().lower() for n in profile.needs if n.strip()]
        tokens = _profile_tokens(profile)
        user_stage = infer_user_stage(profile.arrival_date)

        mentors_top3 = self._mentor_cards(country, country_code, uni, needs, user_stage)
        peers_nearby = self._peer_cards(uni, city)
        cultural_restaurants = self._restaurant_cards(country, country_code, city)
        community_events = self._event_cards(country, country_code, city, user_stage)
        resources = self._resource_cards(needs, city)
        places_of_worship = self._local_place_cards("PlaceOfWorship", "worship", city, tokens, country, needs, uni, user_stage)
        grocery_stores = self._local_place_cards("GroceryStore", "grocery", city, tokens, country, needs, uni, user_stage)
        housing_areas = self._local_place_cards("HousingArea", "housing", city, tokens, country, needs, uni, user_stage)
        exploration_spots = self._local_place_cards("ExplorationSpot", "exploration", city, tokens, country, needs, uni, user_stage)
        transit_tips = self._transit_cards(city, tokens)
        community_groups = self._community_group_cards(country, country_code, uni, city, user_stage)
        tasks_ordered = self.tasks_ordered(city)
        local_entities = self.nodes_by_type("LocalEntity", city)
        guides = self.nodes_by_type("Guide", city)

        student_profile = {
            "full_name": profile.full_name,
            "email": profile.email,
            "country_of_origin": country,
            "home_city": profile.home_city,
            "target_university": uni,
            "target_city": city,
            "needs": needs,
            "interests": profile.interests,
            "new_to_us": bool(profile.new_to_us),
            "arrival_date": profile.arrival_date,
            "user_stage": user_stage,
            "cultural_background": profile.cultural_background,
            "religion_or_observance": profile.religion_or_observance,
            "diet": profile.diet,
            "linkedin_url": profile.linkedin_url,
            "instagram_url": profile.instagram_url,
            "other_social_url": profile.other_social_url,
        }

        evidence_bundle: dict[str, Any] = {
            "graph_source": "markdown",
            "user_stage": user_stage,
            "stage_weights": STAGE_CATEGORY_WEIGHTS.get(user_stage, STAGE_CATEGORY_WEIGHTS["newcomer"]),
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
            "community_groups": [g.model_dump() for g in community_groups],
        }

        subgraph = self._build_profile_subgraph(
            session_id=session_id,
            profile=profile,
            mentors=mentors_top3,
            peers=peers_nearby,
            restaurants=cultural_restaurants,
            events=community_events,
            resources=resources,
            places=[*places_of_worship, *grocery_stores, *housing_areas, *exploration_spots],
            transit_tips=transit_tips,
            community_groups=community_groups,
            tasks=tasks_ordered,
            local_entities=local_entities,
            guides=guides,
        )

        support_coverage_score = self._support_score(resources, mentors_top3, needs)
        cultural_fit_score = self._cultural_fit_score(tokens, places_of_worship, grocery_stores, exploration_spots)
        belonging_score = self._belonging_score(
            mentors_top3=mentors_top3,
            peers_nearby=peers_nearby,
            cultural_restaurants=cultural_restaurants,
            community_events=community_events,
            local_places=[*places_of_worship, *grocery_stores, *housing_areas, *exploration_spots],
            community_groups=community_groups,
            cultural_fit_score=cultural_fit_score,
            user_stage=user_stage,
        )

        best_weekend_outing = ""
        if exploration_spots:
            best_weekend_outing = f"Graph pick: {exploration_spots[0].name}; confirm hours independently."
        elif community_events:
            best_weekend_outing = f"Graph event to research: {community_events[0].name}; verify with organizers."

        return ProfileMatchResponse(
            session_id=session_id,
            user_stage=user_stage,
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
            community_groups=community_groups,
            evidence_bundle=evidence_bundle,
            subgraph=subgraph,
            support_coverage_score=support_coverage_score,
            belonging_score=belonging_score,
            cultural_fit_score=cultural_fit_score,
            best_weekend_outing=best_weekend_outing,
        )

    def tasks_ordered(self, city: str | None = None) -> list[dict[str, Any]]:
        tasks = {node.id: node for node in self.nodes_by_type("Task", city)}
        outgoing: dict[str, list[str]] = defaultdict(list)
        incoming: dict[str, int] = {task_id: 0 for task_id in tasks}

        for task in tasks.values():
            for dep in _as_str_list(task.data.get("depends_on")):
                if dep in tasks:
                    outgoing[dep].append(task.id)
                    incoming[task.id] += 1

        queue = deque(sorted([task_id for task_id, count in incoming.items() if count == 0]))
        ordered: list[MarkdownNode] = []
        while queue:
            task_id = queue.popleft()
            ordered.append(tasks[task_id])
            for child in sorted(outgoing.get(task_id, [])):
                incoming[child] -= 1
                if incoming[child] == 0:
                    queue.append(child)

        seen = {node.id for node in ordered}
        ordered.extend(task for task_id, task in sorted(tasks.items()) if task_id not in seen)

        def priority_value(node: MarkdownNode) -> int:
            try:
                return int(node.data.get("priority", 999))
            except (TypeError, ValueError):
                return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(str(node.data.get("priority", "")).lower(), 999)

        return [
            {
                "id": node.id,
                "name": node.title,
                "priority": priority_value(node),
                "estimated_day_window": str(node.data.get("estimated_day_window") or node.data.get("when") or ""),
                "description": str(node.data.get("description") or ""),
            }
            for node in ordered
        ]

    def pre_arrival_items(self) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        for node in self.nodes.values():
            category = str(node.data.get("category") or "").lower()
            is_checklist = node.type == "PreArrivalChecklist"
            is_pre_arrival_task = node.type == "Task" and category == "pre_arrival"
            if not (is_checklist or is_pre_arrival_task):
                continue
            description = str(data_description) if (data_description := node.data.get("description")) else (
                node.body.splitlines()[0] if node.body else ""
            )
            items.append(
                {
                    "id": node.id,
                    "name": node.title,
                    "description": description,
                    "when": str(node.data.get("when") or "first_week"),
                    "priority": str(node.data.get("priority") or "medium"),
                    "category": str(node.data.get("category") or "pre_arrival"),
                }
            )
        return items

    def _parse_nodes(self) -> tuple[dict[str, MarkdownNode], list[str]]:
        nodes: dict[str, MarkdownNode] = {}
        duplicates: list[str] = []
        if not self.root.exists():
            return nodes, [f"Graph data directory does not exist: {self.root}"]

        for path in sorted(self.root.rglob("*.md")):
            data, body = self._parse_file(path)
            node_id = str(data.get("id") or "").strip()
            node_type = str(data.get("type") or "").strip()
            title = str(data.get("title") or data.get("name") or "").strip()
            city = str(data.get("city") or "").strip()
            wikilinks = [match.strip() for match in WIKILINK_RE.findall(body)]

            if not node_id:
                duplicates.append(f"{path}: missing id")
                continue
            if node_id in nodes:
                duplicates.append(f"Duplicate node id {node_id!r}: {nodes[node_id].path} and {path}")
                continue
            nodes[node_id] = MarkdownNode(
                id=node_id,
                type=node_type,
                title=title,
                city=city,
                data=data,
                body=body,
                path=path,
                wikilinks=wikilinks,
            )
        return nodes, duplicates

    @staticmethod
    def _parse_file(path: Path) -> tuple[dict[str, Any], str]:
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            return {}, raw
        parts = raw.split("---", 2)
        if len(parts) < 3:
            return {}, raw
        frontmatter = yaml.safe_load(parts[1]) or {}
        if not isinstance(frontmatter, dict):
            frontmatter = {}
        return frontmatter, parts[2].strip()

    def _build_edges(self) -> list[MarkdownEdge]:
        edges: list[MarkdownEdge] = []
        title_index = self._title_index()
        seen: set[tuple[str, str, str]] = set()

        def add(from_id: str, to_id: str, kind: str) -> None:
            key = (from_id, to_id, kind)
            if key in seen:
                return
            seen.add(key)
            edges.append(MarkdownEdge(id=f"{kind.lower()}_{len(edges) + 1}", from_id=from_id, to_id=to_id, kind=kind))

        for node in self.nodes.values():
            for target_id in _as_str_list(node.data.get("links_to")):
                add(node.id, target_id, "LINKS_TO")
            for dep_id in _as_str_list(node.data.get("depends_on")):
                add(dep_id, node.id, "PRECEDES")
            for link in node.wikilinks:
                target_id = title_index.get(_norm(link))
                if target_id:
                    add(node.id, target_id, "WIKILINK")
        return edges

    def _validate(self, duplicate_errors: list[str]) -> GraphValidationReport:
        report = GraphValidationReport(errors=list(duplicate_errors))
        title_index = self._title_index()
        types_seen = {node.type for node in self.nodes.values()}

        for required in sorted(REQUIRED_TYPES):
            if required not in types_seen:
                report.errors.append(f"Missing required Markdown node type: {required}")

        for node in self.nodes.values():
            if not node.type:
                report.errors.append(f"{node.path}: missing type")
            if not node.title:
                report.errors.append(f"{node.path}: missing title")
            if node.type not in {"Country", "Need", "PreArrivalChecklist"} and not node.city:
                report.errors.append(f"{node.path}: missing city")

            for target_id in [*_as_str_list(node.data.get("links_to")), *_as_str_list(node.data.get("depends_on"))]:
                if target_id not in self.nodes:
                    report.errors.append(f"{node.path}: broken link to {target_id!r}")
            for link in node.wikilinks:
                if _norm(link) not in title_index:
                    report.errors.append(f"{node.path}: broken wikilink [[{link}]]")

        report.errors.extend(self._task_cycle_errors())
        return report

    def _task_cycle_errors(self) -> list[str]:
        task_ids = {node.id for node in self.nodes.values() if node.type == "Task"}
        visiting: set[str] = set()
        visited: set[str] = set()
        errors: list[str] = []

        def visit(task_id: str, path: list[str]) -> None:
            if task_id in visited:
                return
            if task_id in visiting:
                cycle = " -> ".join([*path, task_id])
                errors.append(f"Task dependency cycle: {cycle}")
                return
            visiting.add(task_id)
            node = self.nodes[task_id]
            for dep_id in _as_str_list(node.data.get("depends_on")):
                if dep_id in task_ids:
                    visit(dep_id, [*path, task_id])
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in sorted(task_ids):
            visit(task_id, [])
        return errors

    def _title_index(self) -> dict[str, str]:
        index: dict[str, str] = {}
        for node in self.nodes.values():
            values = [node.id, node.title, node.path.stem, *_as_str_list(node.data.get("aliases"))]
            for value in values:
                key = _norm(value)
                if key and key not in index:
                    index[key] = node.id
        return index

    def _mentor_cards(self, country: str, country_code: str, uni: str, needs: list[str], user_stage: str) -> list[MentorCard]:
        ranked: list[tuple[float, MarkdownNode, list[str]]] = []
        for node in self.nodes_by_type("Mentor"):
            data = node.data
            shared_country = (
                _text_matches(country, data.get("country_of_origin"))
                or _text_matches(country, data.get("country_tags"))
                or bool(country_code and _text_matches(country_code, data.get("country_tags")))
            )
            shared_uni = _text_matches(uni, [data.get("university"), *_as_str_list(data.get("university_tags"))])
            covered = _lower_set(data.get("needs"))
            overlap = len(covered & set(needs)) / max(len(needs), 1) if needs else 0.5
            trust = float(data.get("trust_score") or 0.0)
            score = min(
                1.0,
                _mentor_score(shared_country=shared_country, shared_uni=shared_uni, need_overlap=overlap, trust_score=trust)
                * _stage_weight(user_stage, "mentor"),
            )
            reasons = []
            if shared_country:
                reasons.append("Shared home country context")
            if shared_uni:
                reasons.append(f"Connected to {uni}")
            if covered:
                reasons.append(f"Need overlap on: {', '.join(sorted(covered))}")
            reasons.append(f"Trust score {trust:.2f}")
            ranked.append((score, node, reasons))

        ranked.sort(key=lambda item: (-item[0], item[1].title))
        cards: list[MentorCard] = []
        for score, node, reasons in ranked[:3]:
            data = node.data
            why = " | ".join(reasons[:2]) if reasons else "Markdown graph match"
            cards.append(
                MentorCard(
                    id=node.id,
                    name=node.title,
                    trust_score=float(data.get("trust_score") or 0.0),
                    languages=_as_str_list(data.get("languages")),
                    match_score=round(score, 4),
                    match_reasons=reasons,
                    why_this_match=why,
                    confidence_score=float(round(score, 4)),
                    email=str(data.get("email") or ""),
                    linkedin_url=str(data.get("linkedin_url") or ""),
                    connect_hint=str(data.get("connect_hint") or ""),
                )
            )
        return cards

    def _peer_cards(self, uni: str, city: str) -> list[PeerCard]:
        cards: list[PeerCard] = []
        for node in self.nodes_by_type("Peer", city):
            data = node.data
            if uni and not _text_matches(uni, [data.get("university"), *_as_str_list(data.get("university_tags"))]):
                continue
            cards.append(
                PeerCard(
                    id=node.id,
                    name=node.title,
                    university=str(data.get("university") or ""),
                    neighborhood=str(data.get("neighborhood") or ""),
                    email=str(data.get("email") or ""),
                    connect_hint=str(data.get("connect_hint") or ""),
                )
            )
        return cards[:8]

    def _restaurant_cards(self, country: str, country_code: str, city: str) -> list[RestaurantCard]:
        cards: list[RestaurantCard] = []
        for node in self.nodes_by_type("Restaurant", city):
            tags = [*_as_str_list(node.data.get("country_tags")), *_as_str_list(node.data.get("diet_tags"))]
            if country and not (_text_matches(country, tags) or (country_code and _text_matches(country_code, tags))):
                continue
            cards.append(
                RestaurantCard(
                    id=node.id,
                    name=node.title,
                    price_level=int(node.data.get("price_level") or 0),
                    distance_km=float(node.data.get("distance_km") or 0.0),
                )
            )
        cards.sort(key=lambda item: (item.distance_km, item.name))
        return cards[:8]

    def _event_cards(self, country: str, country_code: str, city: str, user_stage: str) -> list[EventCard]:
        scored: list[tuple[float, EventCard]] = []
        for node in self.nodes_by_type("Event", city):
            tags = _as_str_list(node.data.get("country_tags"))
            if tags and not (_text_matches(country, tags) or _text_matches(country_code, tags) or _text_matches("US", tags)):
                continue
            data = node.data
            card = EventCard(
                    id=node.id,
                    name=node.title,
                    start_time=str(data.get("start_time") or ""),
                    location=str(data.get("location") or ""),
                    category=str(data.get("category") or ""),
                    notes=str(data.get("notes") or ""),
                    maps_query=str(data.get("maps_query") or ""),
                    maps_link=_maps_url(data),
                )
            stage_score = _stage_weight(user_stage, "event")
            if str(data.get("category") or "").lower() in {"orientation", "arrival"} and user_stage == "newcomer":
                stage_score += 0.08
            scored.append((stage_score, card))
        scored.sort(key=lambda item: (-item[0], item[1].name))
        return [card for _, card in scored[:12]]

    def _resource_cards(self, needs: list[str], city: str) -> list[ResourceCard]:
        cards: list[ResourceCard] = []
        requested = set(needs)
        for node in self.nodes_by_type("Resource", city):
            resource_needs = _lower_set(node.data.get("needs"))
            if requested and resource_needs and not (resource_needs & requested):
                continue
            cards.append(
                ResourceCard(
                    id=node.id,
                    name=node.title,
                    resource_type=str(node.data.get("resource_type") or node.data.get("type") or ""),
                )
            )
        return cards[:12]

    def _local_place_cards(
        self,
        node_type: str,
        place_kind: str,
        city: str,
        tokens: set[str],
        country: str,
        needs: list[str],
        uni: str,
        user_stage: str,
    ) -> list[LocalPlaceCard]:
        scored: list[tuple[float, LocalPlaceCard]] = []
        for node in self.nodes_by_type(node_type, city):
            data = node.data
            tag_keys = ["audience_tags", "diet_tags", "country_tags", "university_tags"]
            tags = [tag for key in tag_keys for tag in _as_str_list(data.get(key))]
            tag_score = _tags_match_score(tags, tokens)
            country_boost = 0.2 if _text_matches(country, data.get("country_tags")) else 0.0
            uni_boost = 0.18 if _text_matches(uni, data.get("university_tags")) else 0.0
            need_boost = 0.15 if any(_text_matches(need, tags) for need in needs) else 0.0
            score = min(1.0, (0.12 + tag_score * 0.65 + country_boost + uni_boost + need_boost) * _stage_weight(user_stage, "local"))
            fallback = "Markdown graph node; verify hours, access, and details before visiting."
            lat, lon = data.get("latitude"), data.get("longitude")
            scored.append(
                (
                    score,
                    LocalPlaceCard(
                        id=node.id,
                        name=node.title,
                        place_kind=place_kind,
                        subtype=str(data.get("subtype") or ""),
                        address=str(data.get("address") or ""),
                        neighborhood=str(data.get("neighborhood") or ""),
                        latitude=float(lat) if lat is not None else None,
                        longitude=float(lon) if lon is not None else None,
                        maps_query=str(data.get("maps_query") or ""),
                        maps_link=_maps_url(data),
                        why_recommended=_why_from_tags(tags, tag_score, fallback),
                    ),
                )
            )
        scored.sort(key=lambda item: (-item[0], item[1].name))
        return [card for _, card in scored[:6]]

    def _transit_cards(self, city: str, tokens: set[str]) -> list[TransitTipCard]:
        scored: list[tuple[float, TransitTipCard]] = []
        for node in self.nodes_by_type("TransitTip", city):
            data = node.data
            blob = f"{node.title} {data.get('route_hint', '')} {data.get('summary', '')}".lower()
            score = 0.25
            if "iit" in tokens and "iit" in blob:
                score += 0.45
            if "green" in blob and ("line" in blob or "cta" in blob):
                score += 0.15
            scored.append(
                (
                    min(1.0, score),
                    TransitTipCard(
                        id=node.id,
                        name=node.title,
                        summary=str(data.get("summary") or ""),
                        route_hint=str(data.get("route_hint") or ""),
                        neighborhood=str(data.get("neighborhood") or ""),
                        maps_link=_maps_url(data),
                    ),
                )
            )
        scored.sort(key=lambda item: (-item[0], item[1].name))
        return [card for _, card in scored[:6]]

    def _community_group_cards(self, country: str, country_code: str, uni: str, city: str, user_stage: str) -> list[CommunityGroupCard]:
        scored: list[tuple[float, CommunityGroupCard]] = []
        for node in self.nodes_by_type("CommunityGroup", city):
            tags = [*_as_str_list(node.data.get("country_tags")), *_as_str_list(node.data.get("university_tags"))]
            if tags and not (_text_matches(country, tags) or _text_matches(country_code, tags) or _text_matches(uni, tags)):
                continue
            card = CommunityGroupCard(
                    id=node.id,
                    name=node.title,
                    platform=str(node.data.get("platform") or ""),
                    join_url=str(node.data.get("join_url") or ""),
                    why_recommended=f"Matched by city, university, country, and {user_stage} journey stage. Verify moderation before joining.",
                )
            scored.append((_stage_weight(user_stage, "community_group"), card))
        scored.sort(key=lambda item: (-item[0], item[1].name))
        return [card for _, card in scored[:8]]

    def _build_profile_subgraph(
        self,
        *,
        session_id: str,
        profile: ProfileMatchRequest,
        mentors: list[MentorCard],
        peers: list[PeerCard],
        restaurants: list[RestaurantCard],
        events: list[EventCard],
        resources: list[ResourceCard],
        places: list[LocalPlaceCard],
        transit_tips: list[TransitTipCard],
        community_groups: list[CommunityGroupCard],
        tasks: list[dict[str, Any]],
        local_entities: list[MarkdownNode],
        guides: list[MarkdownNode],
    ) -> Subgraph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        seen_nodes: set[str] = set()
        seen_edges: set[tuple[str, str]] = set()
        student_node_id = f"student_{session_id}"

        def add_node(
            node_id: str,
            label: str,
            group: str,
            subtitle: str | None = None,
            *,
            address: str | None = None,
            maps_query: str | None = None,
            maps_link: str | None = None,
            why_recommended: str | None = None,
        ) -> None:
            if node_id in seen_nodes:
                return
            seen_nodes.add(node_id)
            nodes.append(
                GraphNode(
                    id=node_id,
                    label=label,
                    group=group,
                    subtitle=subtitle,
                    address=address,
                    maps_query=maps_query or None,
                    maps_link=maps_link or None,
                    why_recommended=why_recommended,
                )
            )

        def add_edge(from_id: str, to_id: str, prefix: str) -> None:
            if from_id not in seen_nodes or to_id not in seen_nodes:
                return
            key = (from_id, to_id)
            if key in seen_edges:
                return
            seen_edges.add(key)
            edges.append(GraphEdge(id=f"{prefix}_{len(edges) + 1}", from_=from_id, to=to_id))

        display_name = profile.full_name.strip() or "You"
        add_node(
            student_node_id,
            f"{display_name} | {profile.home_city.strip()}",
            "student",
            f"{profile.country_of_origin.strip()} -> {profile.target_university.strip()}",
        )

        for mentor in mentors:
            add_node(mentor.id, mentor.name, "mentor", f"score {mentor.match_score:.2f}")
            add_edge(student_node_id, mentor.id, "sm")
        for peer in peers:
            add_node(peer.id, peer.name, "peer", peer.neighborhood)
            add_edge(student_node_id, peer.id, "sp")
        for restaurant in restaurants:
            add_node(restaurant.id, restaurant.name, "restaurant", f"{restaurant.distance_km} km")
            add_edge(student_node_id, restaurant.id, "sr")
        for event in events:
            add_node(event.id, event.name, "event", event.category, maps_query=event.maps_query, maps_link=event.maps_link, why_recommended=event.notes or None)
            add_edge(student_node_id, event.id, "sev")
        for resource in resources:
            add_node(resource.id, resource.name, "resource", resource.resource_type)
            add_edge(student_node_id, resource.id, "sres")
        for place in places:
            group = {
                "worship": "place_worship",
                "grocery": "grocery",
                "housing": "housing_area",
                "exploration": "exploration",
            }.get(place.place_kind, "local_entity")
            add_node(
                place.id,
                place.name,
                group,
                place.neighborhood or place.subtype,
                address=place.address or None,
                maps_query=place.maps_query or None,
                maps_link=place.maps_link or None,
                why_recommended=place.why_recommended or None,
            )
            add_edge(student_node_id, place.id, "sl")
        for tip in transit_tips:
            add_node(tip.id, tip.name, "transit_tip", tip.neighborhood or "Transit", maps_link=tip.maps_link or None, why_recommended=tip.summary or None)
            add_edge(student_node_id, tip.id, "st")
        for group in community_groups:
            add_node(group.id, group.name, "community_group", group.platform, maps_link=group.join_url or None, why_recommended=group.why_recommended)
            add_edge(student_node_id, group.id, "sg")
        for task in tasks:
            add_node(task["id"], str(task["name"]), "task", str(task.get("estimated_day_window") or ""))
        for index in range(len(tasks) - 1):
            add_edge(tasks[index]["id"], tasks[index + 1]["id"], "task")
        for entity in local_entities:
            add_node(
                entity.id,
                entity.title,
                "local_entity",
                str(entity.data.get("subtype") or entity.data.get("neighborhood") or ""),
                address=str(entity.data.get("address") or "") or None,
                maps_query=str(entity.data.get("maps_query") or "") or None,
                maps_link=_maps_url(entity.data) or None,
            )
            add_edge(student_node_id, entity.id, "sle")
        for guide in guides:
            add_node(guide.id, guide.title, "guide", str(guide.data.get("category") or "Guide"))
            add_edge(student_node_id, guide.id, "sguide")

        known_ids = seen_nodes
        for edge in self.edges:
            if edge.from_id in known_ids and edge.to_id in known_ids:
                add_edge(edge.from_id, edge.to_id, edge.kind.lower())

        return Subgraph(nodes=nodes, edges=edges)

    @staticmethod
    def _support_score(resources: list[ResourceCard], mentors: list[MentorCard], needs: list[str]) -> float:
        need_count = max(len(needs), 1)
        res_score = min(1.0, len(resources) / max(need_count * 2, 1))
        mentor_cov = min(1.0, len(mentors) / 3) if mentors else 0.0
        return round(0.55 * res_score + 0.45 * mentor_cov, 3)

    @staticmethod
    def _cultural_fit_score(tokens: set[str], *groups: list[LocalPlaceCard]) -> float:
        scores = []
        for cards in groups:
            if not cards:
                continue
            top = cards[0]
            scores.append(_tags_match_score([top.subtype, top.why_recommended, top.name], tokens))
        return round(sum(scores) / len(scores), 3) if scores else 0.0

    @staticmethod
    def _belonging_score(
        *,
        mentors_top3: list[MentorCard],
        peers_nearby: list[PeerCard],
        cultural_restaurants: list[RestaurantCard],
        community_events: list[EventCard],
        local_places: list[LocalPlaceCard],
        community_groups: list[CommunityGroupCard],
        cultural_fit_score: float,
        user_stage: str,
    ) -> float:
        mentor_cov = min(1.0, len(mentors_top3) / 3) if mentors_top3 else 0.0
        peer_p = min(1.0, len(peers_nearby) / 5)
        event_p = min(1.0, len(community_events) / 5)
        food_p = min(1.0, len(cultural_restaurants) / 5)
        local_p = min(1.0, len(local_places) / 14)
        group_p = min(1.0, len(community_groups) / 3)
        weights = {
            "newcomer": (0.16, 0.12, 0.12, 0.28, 0.16, 0.08, 0.10),
            "settler": (0.24, 0.18, 0.12, 0.14, 0.12, 0.18, 0.04),
            "local": (0.16, 0.24, 0.10, 0.10, 0.22, 0.20, 0.08),
            "mentor": (0.14, 0.24, 0.08, 0.08, 0.22, 0.22, 0.08),
        }.get(user_stage, (0.16, 0.12, 0.12, 0.28, 0.16, 0.08, 0.10))
        peer_w, event_w, food_w, mentor_w, local_w, group_w, fit_w = weights
        return round(
            peer_w * peer_p
            + event_w * event_p
            + food_w * food_p
            + mentor_w * mentor_cov
            + local_w * local_p
            + group_w * group_p
            + fit_w * cultural_fit_score,
            3,
        )
