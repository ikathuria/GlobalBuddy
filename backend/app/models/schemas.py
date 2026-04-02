"""Pydantic models for /v1 API contracts (aligned with docs/api-spec.md)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# --- Profile match ---
class ProfileMatchRequest(BaseModel):
    country_of_origin: str
    home_city: str
    target_university: str
    target_city: str
    needs: list[str]
    interests: list[str] = Field(default_factory=list)
    cultural_background: str = Field(default="", description="Optional; used for deterministic cultural-fit ranking.")
    religion_or_observance: str = Field(
        default="",
        description="Optional; e.g. Hindu, Muslim, Sikh, Christian — matched to graph tags.",
    )
    diet: str = Field(default="", description="Optional; e.g. vegetarian, halal — matched to graph diet tags.")


class MentorCard(BaseModel):
    id: str
    name: str
    trust_score: float
    languages: list[str]
    match_score: float
    match_reasons: list[str]
    why_this_match: str = Field(
        default="",
        description="Single-sentence rationale from graph signals (deterministic).",
    )
    confidence_score: float = Field(
        default=0.0,
        description="Same as match_score — surfaced for UI badges.",
    )
    email: str = Field(default="", description="From Neo4j Mentor.email — demo-safe placeholder.")
    linkedin_url: str = Field(default="", description="Optional profile URL from graph.")
    connect_hint: str = Field(
        default="",
        description="Short guidance for how to reach out (stored on Mentor in Neo4j).",
    )


class PeerCard(BaseModel):
    id: str
    name: str
    university: str
    neighborhood: str
    email: str = Field(default="", description="From Neo4j Peer.email when present.")
    connect_hint: str = Field(default="", description="How to connect with this peer (graph).")


class RestaurantCard(BaseModel):
    id: str
    name: str
    price_level: int
    distance_km: float


class EventCard(BaseModel):
    id: str
    name: str
    start_time: str
    location: str
    category: str
    notes: str = Field(default="", description="Seeded disclaimer or context; not a live schedule.")
    maps_query: str = Field(default="", description="For Google Maps search / embed.")
    maps_link: str = Field(default="", description="Optional prebuilt maps URL.")


class LocalPlaceCard(BaseModel):
    """Worship, grocery, housing cluster, or downtown exploration — from Neo4j local intelligence nodes."""

    id: str
    name: str
    place_kind: str = Field(description="worship | grocery | housing | exploration")
    subtype: str = Field(default="", description="temple, mosque, market, etc.")
    address: str = ""
    neighborhood: str = ""
    latitude: float | None = None
    longitude: float | None = None
    maps_query: str = ""
    maps_link: str = ""
    why_recommended: str = Field(default="", description="Deterministic rationale from graph tags and profile.")


class TransitTipCard(BaseModel):
    id: str
    name: str
    summary: str
    route_hint: str
    neighborhood: str = ""
    maps_link: str = ""


class ResourceCard(BaseModel):
    id: str
    name: str
    resource_type: str


class GraphNode(BaseModel):
    id: str
    label: str
    group: str
    subtitle: str | None = None
    address: str | None = None
    maps_query: str | None = None
    maps_link: str | None = None
    why_recommended: str | None = None


class GraphEdge(BaseModel):
    model_config = {"populate_by_name": True}

    id: str
    from_: str = Field(alias="from")
    to: str


class Subgraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ProfileMatchResponse(BaseModel):
    session_id: str
    mentors_top3: list[MentorCard]
    peers_nearby: list[PeerCard]
    cultural_restaurants: list[RestaurantCard]
    community_events: list[EventCard]
    resources: list[ResourceCard]
    places_of_worship: list[LocalPlaceCard] = Field(default_factory=list)
    grocery_stores: list[LocalPlaceCard] = Field(default_factory=list)
    housing_areas: list[LocalPlaceCard] = Field(default_factory=list)
    exploration_spots: list[LocalPlaceCard] = Field(default_factory=list)
    transit_tips: list[TransitTipCard] = Field(default_factory=list)
    evidence_bundle: dict[str, Any]
    subgraph: Subgraph
    support_coverage_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How well resources + mentors cover stated needs (deterministic).",
    )
    belonging_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Composite 'connectedness' from peers, events, food, mentors.",
    )
    cultural_fit_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overlap of profile signals with local worship/grocery/event tags (deterministic).",
    )
    best_weekend_outing: str = Field(
        default="",
        description="Single graph-grounded suggestion from exploration + events (deterministic).",
    )


# --- Plan ---
class PlanGenerateRequest(BaseModel):
    session_id: UUID
    student_profile: dict[str, Any] = Field(default_factory=dict)
    evidence_bundle: dict[str, Any] = Field(default_factory=dict)


class PlanStep(BaseModel):
    day_range: str
    action: str
    entities: list[str]
    dependency_reason: str
    source_node_ids: list[str] = Field(default_factory=list)


class PlanGenerateResponse(BaseModel):
    plan_title: str
    best_next_action: str | None = None
    steps: list[PlanStep]
    priority_contacts: list[str]
    warnings: list[str]
    confidence: float
    fallback_used: bool = False
    llm_provider: str = "unknown"


# --- Bridge ---
class BridgeExplainRequest(BaseModel):
    session_id: UUID | None = None
    term: str
    home_country: str
    context: str


class BridgeExplainResponse(BaseModel):
    term: str
    plain_explanation: str
    home_context_analogy: str
    common_mistakes: list[str]
    what_to_do_next: list[str]
    fallback_used: bool = False
    llm_provider: str


# --- Graph ---
class GraphSubgraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    highlights: list[str] = Field(default_factory=list)
