from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProfileMatchRequest(BaseModel):
    country_of_origin: str = Field(min_length=2)
    home_city: str = Field(min_length=1)
    target_university: str = Field(min_length=2)
    target_city: str = Field(min_length=2)
    needs: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)


class MentorMatch(BaseModel):
    id: str
    name: str
    score: float
    trust_score: float
    response_rate: float
    languages: list[str] = Field(default_factory=list)
    match_reasons: list[str] = Field(default_factory=list)


class PeerMatch(BaseModel):
    id: str
    name: str
    neighborhood: str | None = None


class RestaurantMatch(BaseModel):
    id: str
    name: str
    distance_km: float | None = None
    price_level: int | None = None


class EventMatch(BaseModel):
    id: str
    name: str
    start_time: str
    location: str | None = None
    category: str | None = None


class ResourceMatch(BaseModel):
    id: str
    name: str
    type: str | None = None
    url: str | None = None


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    metadata: dict = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str


class GraphSubgraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class ProfileMatchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str
    mentors_top3: list[MentorMatch] = Field(default_factory=list)
    peers_nearby: list[PeerMatch] = Field(default_factory=list)
    cultural_restaurants: list[RestaurantMatch] = Field(default_factory=list)
    community_events: list[EventMatch] = Field(default_factory=list)
    resources: list[ResourceMatch] = Field(default_factory=list)
    subgraph: GraphSubgraph


class PlanGenerateRequest(BaseModel):
    session_id: str = Field(min_length=3)
    student_profile: dict = Field(default_factory=dict)
    evidence_bundle: dict = Field(default_factory=dict)


class PlanStep(BaseModel):
    day_range: str
    action: str
    entities: list[str] = Field(default_factory=list)
    dependency_reason: str
    source_node_ids: list[str] = Field(default_factory=list)


class PlanGenerateResponse(BaseModel):
    plan_title: str
    steps: list[PlanStep] = Field(default_factory=list)
    priority_contacts: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class BridgeExplainRequest(BaseModel):
    session_id: str = Field(min_length=3)
    term: str = Field(min_length=2)
    home_country: str = Field(min_length=2)
    context: str = Field(min_length=2)


class BridgeExplainResponse(BaseModel):
    term: str
    plain_explanation: str
    home_context_analogy: str
    common_mistakes: list[str] = Field(default_factory=list)
    what_to_do_next: list[str] = Field(default_factory=list)
