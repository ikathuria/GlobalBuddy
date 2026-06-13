"""Social layer tests: connect, mentor intro (email privacy), and request listing.

Auth + DB are mocked so these run without Neon or a JWKS provider: we patch the
principal, the repository calls, and the email sender, and point app.state.db at
a stub that reports enabled.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.auth import AuthPrincipal

MENTOR_EMAIL = "priya.mentor@example.test"


class _DB:
    enabled = True


def _principal() -> AuthPrincipal:
    return AuthPrincipal(claims={"sub": "auth-123", "email": "stu@example.test", "name": "Test Student"})


def _profile() -> dict:
    return {"id": "profile-1", "full_name": "Test Student", "email": "stu@example.test"}


def _row(**overrides) -> dict:
    row = {
        "id": "req-1",
        "kind": "connection",
        "target_node_id": "peer_arjun_mehta",
        "target_name": "Arjun Mehta",
        "target_role": "Peer",
        "status": "pending",
        "email_sent": False,
        "created_at": datetime(2026, 6, 12, tzinfo=timezone.utc),
    }
    row.update(overrides)
    return row


@pytest.fixture
def social_env(api_client, monkeypatch):
    """Patch auth, db, and repository calls for authenticated social-route tests."""
    monkeypatch.setattr("app.routers.social.require_principal", lambda _request: _principal())
    monkeypatch.setattr(api_client.app.state, "db", _DB())

    async def _get_profile(_db, _claims):
        return _profile()

    monkeypatch.setattr("app.db.repositories.get_or_create_profile_from_claims", _get_profile)
    return monkeypatch


# ── Auth gate (no patching) ───────────────────────────────────────────────────

def test_connect_requires_auth(api_client) -> None:
    r = api_client.post("/v1/social/connect", json={"target_node_id": "peer_arjun_mehta"})
    assert r.status_code == 401


def test_intro_requires_auth(api_client) -> None:
    r = api_client.post("/v1/social/intro-request", json={"mentor_node_id": "mentor_priya_shah"})
    assert r.status_code == 401


def test_requests_list_requires_auth(api_client) -> None:
    r = api_client.get("/v1/social/requests")
    assert r.status_code == 401


# ── Connect ───────────────────────────────────────────────────────────────────

def test_connect_creates_request(api_client, social_env) -> None:
    async def _create(_db, **kwargs):
        assert kwargs["kind"] == "connection"
        assert kwargs["requester_id"] == "profile-1"
        return _row(target_node_id=kwargs["target_node_id"]), True

    social_env.setattr("app.db.repositories.create_social_request", _create)

    r = api_client.post(
        "/v1/social/connect",
        json={"target_node_id": "peer_arjun_mehta", "target_name": "Arjun Mehta", "target_role": "Peer"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["kind"] == "connection"
    assert data["target_node_id"] == "peer_arjun_mehta"
    assert data["status"] == "pending"


# ── Mentor intro ────────────────────────────────────────────────────────────────

def test_intro_sends_email_without_exposing_mentor_address(api_client, social_env) -> None:
    sent: dict = {}

    async def _create(_db, **kwargs):
        assert kwargs["kind"] == "intro"
        return _row(kind="intro", target_node_id="mentor_priya_shah", target_name="Priya Shah", target_role="Mentor"), True

    async def _send_email(_settings, *, to, subject, html, reply_to=None):
        sent["to"] = to
        sent["reply_to"] = reply_to
        return True

    marked: dict = {}

    async def _mark(_db, *, request_id):
        marked["id"] = request_id

    social_env.setattr("app.db.repositories.create_social_request", _create)
    social_env.setattr("app.services.email_service.send_email", _send_email)
    social_env.setattr("app.db.repositories.mark_social_request_email_sent", _mark)

    r = api_client.post("/v1/social/intro-request", json={"mentor_node_id": "mentor_priya_shah"})
    assert r.status_code == 200

    # The mentor's address is emailed server-side but must never reach the client.
    assert MENTOR_EMAIL not in r.text
    assert sent["to"] == MENTOR_EMAIL
    assert sent["reply_to"] == "stu@example.test"

    data = r.json()
    assert data["kind"] == "intro"
    assert data["email_sent"] is True
    assert marked["id"] == "req-1"


def test_intro_unknown_mentor_returns_404(api_client, social_env) -> None:
    r = api_client.post("/v1/social/intro-request", json={"mentor_node_id": "mentor_does_not_exist"})
    assert r.status_code == 404


def test_intro_skips_email_on_duplicate(api_client, social_env) -> None:
    calls = {"sent": 0}

    async def _create(_db, **kwargs):
        # Simulate a pre-existing request: created=False.
        return _row(kind="intro", target_node_id="mentor_priya_shah", target_name="Priya Shah"), False

    async def _send_email(_settings, **_kwargs):
        calls["sent"] += 1
        return True

    social_env.setattr("app.db.repositories.create_social_request", _create)
    social_env.setattr("app.services.email_service.send_email", _send_email)

    r = api_client.post("/v1/social/intro-request", json={"mentor_node_id": "mentor_priya_shah"})
    assert r.status_code == 200
    assert calls["sent"] == 0  # no duplicate email on a repeat request


# ── Listing ─────────────────────────────────────────────────────────────────────

def test_list_requests_returns_items(api_client, social_env) -> None:
    async def _list(_db, *, requester_id):
        assert requester_id == "profile-1"
        return [
            _row(),
            _row(id="req-2", kind="intro", target_node_id="mentor_priya_shah", target_name="Priya Shah", status="accepted", email_sent=True),
        ]

    social_env.setattr("app.db.repositories.list_social_requests", _list)

    r = api_client.get("/v1/social/requests")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 2
    assert items[1]["status"] == "accepted"
    assert items[1]["email_sent"] is True
