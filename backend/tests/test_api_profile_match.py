"""POST /v1/profile/match response shape (router + mocked agent)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.models.schemas import GraphEdge, GraphNode, ProfileMatchResponse, Subgraph


@pytest.fixture
def fake_match_response() -> ProfileMatchResponse:
    return ProfileMatchResponse(
        session_id="550e8400-e29b-41d4-a716-446655440000",
        mentors_top3=[],
        peers_nearby=[],
        cultural_restaurants=[],
        community_events=[],
        resources=[],
        evidence_bundle={
            "mentors": [],
            "tasks_ordered": [],
            "student_profile": {"country_of_origin": "India"},
        },
        subgraph=Subgraph(
            nodes=[GraphNode(id="n1", label="You", group="student", subtitle="India → Illinois Institute of Technology")],
            edges=[],
        ),
        support_coverage_score=0.5,
        belonging_score=0.4,
        cultural_fit_score=0.42,
        best_weekend_outing="Graph pick: Example",
    )


def test_profile_match_endpoint_shape(api_client: object, monkeypatch: pytest.MonkeyPatch, fake_match_response: ProfileMatchResponse) -> None:
    monkeypatch.setattr("app.routers.profile.run_profile_match", AsyncMock(return_value=fake_match_response))

    r = api_client.post(
        "/v1/profile/match",
        json={
            "country_of_origin": "India",
            "home_city": "Bengaluru",
            "target_university": "Illinois Institute of Technology",
            "target_city": "Chicago",
            "needs": ["banking"],
            "interests": ["food"],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"]
    assert "mentors_top3" in data
    assert "peers_nearby" in data
    assert "cultural_restaurants" in data
    assert "community_events" in data
    assert "resources" in data
    assert "evidence_bundle" in data
    assert "subgraph" in data and "nodes" in data["subgraph"] and "edges" in data["subgraph"]
    assert "support_coverage_score" in data
    assert "belonging_score" in data
    assert "cultural_fit_score" in data
    assert "best_weekend_outing" in data
    assert "places_of_worship" in data


def test_subgraph_edge_from_alias_roundtrip() -> None:
    e = GraphEdge(id="e1", **{"from": "a", "to": "b"})
    dumped = e.model_dump(mode="json", by_alias=True)
    assert dumped.get("from") == "a"
