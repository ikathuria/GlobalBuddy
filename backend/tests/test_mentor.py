"""Mentor system tests: public directory (seed merge), opt-in gating, rating."""

from __future__ import annotations

import pytest

from app.auth import AuthPrincipal


class _DB:
    enabled = True


def _principal() -> AuthPrincipal:
    return AuthPrincipal(claims={"sub": "auth-1", "email": "s@example.test", "name": "Sam"})


@pytest.fixture
def mentor_env(api_client, monkeypatch):
    monkeypatch.setattr("app.routers.mentor.require_principal", lambda _r: _principal())
    monkeypatch.setattr(api_client.app.state, "db", _DB())
    return monkeypatch


# ── Public directory ────────────────────────────────────────────────────────────

def test_directory_is_public_and_lists_seed_mentors(api_client) -> None:
    r = api_client.get("/v1/mentors")
    assert r.status_code == 200
    items = r.json()["items"]
    names = {m["name"] for m in items}
    assert "Priya Shah" in names
    seed = next(m for m in items if m["name"] == "Priya Shah")
    assert seed["source"] == "seed"
    assert seed["can_rate"] is False
    assert seed["country"].lower() == "india"


def test_directory_filters_by_country(api_client) -> None:
    assert any(m["name"] == "Priya Shah" for m in api_client.get("/v1/mentors", params={"country": "India"}).json()["items"])
    assert all(m["name"] != "Priya Shah" for m in api_client.get("/v1/mentors", params={"city": "Boston"}).json()["items"])


# ── Auth gates ────────────────────────────────────────────────────────────────

def test_opt_in_requires_auth(api_client) -> None:
    assert api_client.post("/v1/mentors/opt-in", json={}).status_code == 401


def test_me_requires_auth(api_client) -> None:
    assert api_client.get("/v1/mentors/me").status_code == 401


def test_rate_requires_auth(api_client) -> None:
    assert api_client.post("/v1/mentors/abc/rate", json={"rating": 5}).status_code == 401


# ── Opt-in gating ───────────────────────────────────────────────────────────────

def test_opt_in_blocked_for_newcomer(api_client, mentor_env) -> None:
    async def _profile(_db, _claims):
        return {"id": "p1", "stage": "newcomer"}

    mentor_env.setattr("app.db.repositories.get_or_create_profile_from_claims", _profile)
    r = api_client.post("/v1/mentors/opt-in", json={"expertise": ["banking"], "bio": "hi"})
    assert r.status_code == 403


def test_opt_in_succeeds_for_settler(api_client, mentor_env) -> None:
    async def _profile(_db, _claims):
        return {"id": "p1", "stage": "settler"}

    async def _opt_in(_db, **kwargs):
        assert kwargs["user_id"] == "p1"
        return {"expertise": kwargs["expertise"], "availability": "available", "bio": kwargs["bio"]}

    mentor_env.setattr("app.db.repositories.get_or_create_profile_from_claims", _profile)
    mentor_env.setattr("app.db.repositories.opt_in_mentor", _opt_in)

    r = api_client.post("/v1/mentors/opt-in", json={"expertise": ["banking", "housing"], "bio": "Happy to help"})
    assert r.status_code == 200
    data = r.json()
    assert data["stage"] == "mentor"
    assert data["expertise"] == ["banking", "housing"]


# ── Rating ──────────────────────────────────────────────────────────────────────

def test_rate_unknown_mentor_404(api_client, mentor_env) -> None:
    async def _profile(_db, _claims):
        return {"id": "reviewer-1", "stage": "newcomer"}

    async def _get_mentor(_db, *, user_id):
        return None

    mentor_env.setattr("app.db.repositories.get_or_create_profile_from_claims", _profile)
    mentor_env.setattr("app.db.repositories.get_mentor_profile", _get_mentor)

    r = api_client.post("/v1/mentors/mentor-x/rate", json={"rating": 4})
    assert r.status_code == 404


def test_rate_updates_average(api_client, mentor_env) -> None:
    async def _profile(_db, _claims):
        return {"id": "reviewer-1", "stage": "newcomer"}

    async def _get_mentor(_db, *, user_id):
        return {"user_id": user_id}

    async def _add_rating(_db, **kwargs):
        assert kwargs["rating"] == 5
        return 4.5

    mentor_env.setattr("app.db.repositories.get_or_create_profile_from_claims", _profile)
    mentor_env.setattr("app.db.repositories.get_mentor_profile", _get_mentor)
    mentor_env.setattr("app.db.repositories.add_mentor_rating", _add_rating)

    r = api_client.post("/v1/mentors/mentor-9/rate", json={"rating": 5, "comment": "great"})
    assert r.status_code == 200
    assert r.json()["rating"] == 4.5


def test_cannot_rate_self(api_client, mentor_env) -> None:
    async def _profile(_db, _claims):
        return {"id": "same-id", "stage": "mentor"}

    mentor_env.setattr("app.db.repositories.get_or_create_profile_from_claims", _profile)
    r = api_client.post("/v1/mentors/same-id/rate", json={"rating": 5})
    assert r.status_code == 400
