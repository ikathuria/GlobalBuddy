"""Multi-city coverage (M15): Boston and NYC return their own graph data."""

from __future__ import annotations

from pathlib import Path

from app.models.schemas import ProfileMatchRequest
from app.services.markdown_graph import MarkdownGraphService


def _service() -> MarkdownGraphService:
    return MarkdownGraphService(Path(__file__).resolve().parents[2] / "data" / "graph")


def _profile(city: str, university: str) -> ProfileMatchRequest:
    return ProfileMatchRequest(
        full_name="Test Student",
        email="t@example.test",
        country_of_origin="India",
        home_city="Mumbai",
        target_university=university,
        target_city=city,
        needs=["banking", "housing", "community"],
        interests=["food"],
        arrival_date="2026-08-20",
        religion_or_observance="Hindu",
        diet="vegetarian",
    )


def test_graph_validates_with_three_cities() -> None:
    service = _service()
    assert service.validation.ok, service.validation.errors
    cities = {n.city for n in service.nodes.values() if n.city}
    assert {"Chicago", "Boston", "New York"} <= cities


def test_boston_match_returns_boston_local_data() -> None:
    service = _service()
    result = service.profile_match(_profile("Boston", "Northeastern University"))

    # Peers/places/groups are city-filtered, so they must be Boston nodes.
    assert result.peers_nearby
    assert all("boston" in p.id for p in result.peers_nearby)
    local = [*result.places_of_worship, *result.grocery_stores, *result.housing_areas, *result.exploration_spots]
    assert len(local) >= 6
    assert all("boston" in p.id for p in local)
    assert any("boston" in g.id for g in result.community_groups)


def test_nyc_match_returns_nyc_local_data() -> None:
    service = _service()
    result = service.profile_match(_profile("New York", "New York University"))
    assert result.peers_nearby
    assert all("nyc" in p.id for p in result.peers_nearby)
    local = [*result.places_of_worship, *result.grocery_stores, *result.housing_areas, *result.exploration_spots]
    assert len(local) >= 6
    assert all("nyc" in p.id for p in local)


def test_each_city_has_at_least_five_mentors() -> None:
    service = _service()
    for prefix in ("mentor_boston", "mentor_nyc"):
        mentors = [n for n in service.nodes.values() if n.type == "Mentor" and n.id.startswith(prefix)]
        assert len(mentors) >= 5, f"{prefix}: {len(mentors)}"


def test_feed_is_city_scoped() -> None:
    service = _service()
    boston_feed = service.feed_items(city="Boston")
    assert boston_feed
    assert all(item["city"] == "Boston" for item in boston_feed)
    assert any(item["type"] == "guide" for item in boston_feed)
