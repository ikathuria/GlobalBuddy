"""Regression tests: new_to_us=False skip behavior.

Verifies the API contract that downstream callers (frontend) rely on to decide
whether to skip Step 2 (AI Plan). The skip logic lives in the frontend, so these
tests confirm the field is present and correctly typed in the response.
"""

from __future__ import annotations

import uuid

import pytest


_PROFILE_BASE = {
    "full_name": "Priya Sharma",
    "email": "priya@example.com",
    "country_of_origin": "India",
    "home_city": "Bengaluru",
    "target_university": "Illinois Institute of Technology",
    "target_city": "Chicago",
    "needs": ["housing", "banking"],
}


def test_new_to_us_true_is_default(api_client: object) -> None:
    """Omitting new_to_us defaults to True — first-time arrival."""
    r = api_client.post("/v1/profile/match", json=_PROFILE_BASE)
    assert r.status_code == 200
    profile = r.json()["evidence_bundle"]["student_profile"]
    assert profile["new_to_us"] is True


def test_new_to_us_false_is_preserved(api_client: object) -> None:
    """new_to_us=False must survive the round-trip; frontend uses it to skip Step 2."""
    payload = {**_PROFILE_BASE, "new_to_us": False}
    r = api_client.post("/v1/profile/match", json=payload)
    assert r.status_code == 200
    data = r.json()
    # Field must be present in evidence_bundle so the frontend can read it
    profile = data["evidence_bundle"]["student_profile"]
    assert profile["new_to_us"] is False


def test_new_to_us_false_session_still_usable(api_client: object) -> None:
    """A session from a new_to_us=False profile can still generate a plan if requested."""
    payload = {**_PROFILE_BASE, "new_to_us": False}
    match_r = api_client.post("/v1/profile/match", json=payload)
    assert match_r.status_code == 200
    session_id = match_r.json()["session_id"]

    # Plan generation must still work even though frontend would skip it
    plan_r = api_client.post(
        "/v1/plan/generate",
        json={"session_id": session_id},
    )
    assert plan_r.status_code == 200
    plan = plan_r.json()
    assert "steps" in plan
    assert "plan_title" in plan


def test_new_to_us_true_session_plan_flow(api_client: object) -> None:
    """Baseline: new_to_us=True → profile match → plan generate both return 200."""
    payload = {**_PROFILE_BASE, "new_to_us": True}
    match_r = api_client.post("/v1/profile/match", json=payload)
    assert match_r.status_code == 200
    session_id = match_r.json()["session_id"]

    plan_r = api_client.post(
        "/v1/plan/generate",
        json={"session_id": session_id},
    )
    assert plan_r.status_code == 200


def test_new_to_us_false_response_has_required_fields(api_client: object) -> None:
    """Response shape is identical regardless of new_to_us value."""
    for flag in (True, False):
        r = api_client.post("/v1/profile/match", json={**_PROFILE_BASE, "new_to_us": flag})
        assert r.status_code == 200
        data = r.json()
        for field in ("session_id", "mentors_top3", "peers_nearby", "evidence_bundle", "subgraph"):
            assert field in data, f"Missing {field!r} when new_to_us={flag}"
