"""Notification tests: auth gates, listing/unread, and social-action triggers."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.auth import AuthPrincipal


class _DB:
    enabled = True


def _principal() -> AuthPrincipal:
    return AuthPrincipal(claims={"sub": "auth-1", "email": "s@example.test", "name": "Sam"})


def _notif(**overrides) -> dict:
    row = {
        "id": "n1",
        "type": "intro_sent",
        "title": "Intro requested",
        "body": "We've reached out.",
        "read": False,
        "created_at": datetime(2026, 6, 12, tzinfo=timezone.utc),
    }
    row.update(overrides)
    return row


# ── Auth gates ──────────────────────────────────────────────────────────────────

def test_notifications_requires_auth(api_client) -> None:
    assert api_client.get("/v1/notifications").status_code == 401


def test_mark_read_requires_auth(api_client) -> None:
    assert api_client.post("/v1/notifications/n1/read").status_code == 401


# ── Listing ──────────────────────────────────────────────────────────────────────

def test_list_returns_items_and_unread(api_client, monkeypatch) -> None:
    monkeypatch.setattr("app.routers.notifications.require_principal", lambda _r: _principal())
    monkeypatch.setattr(api_client.app.state, "db", _DB())

    async def _profile(_db, _claims):
        return {"id": "p1"}

    async def _list(_db, *, user_id, limit=30):
        return [_notif(), _notif(id="n2", read=True)]

    async def _unread(_db, *, user_id):
        return 1

    monkeypatch.setattr("app.db.repositories.get_or_create_profile_from_claims", _profile)
    monkeypatch.setattr("app.db.repositories.list_notifications", _list)
    monkeypatch.setattr("app.db.repositories.count_unread_notifications", _unread)

    r = api_client.get("/v1/notifications")
    assert r.status_code == 200
    data = r.json()
    assert data["unread"] == 1
    assert len(data["items"]) == 2
    assert data["items"][0]["title"] == "Intro requested"


# ── Trigger: sending an intro creates a notification ─────────────────────────────

def test_intro_request_creates_notification(api_client, monkeypatch) -> None:
    monkeypatch.setattr("app.routers.social.require_principal", lambda _r: _principal())
    monkeypatch.setattr(api_client.app.state, "db", _DB())

    created_notifs: list[dict] = []

    async def _profile(_db, _claims):
        return {"id": "p1", "full_name": "Sam", "email": "s@example.test"}

    async def _create_request(_db, **kwargs):
        from datetime import datetime, timezone as tz
        return {
            "id": "req-1", "kind": "intro", "target_node_id": kwargs["target_node_id"],
            "target_name": kwargs["target_name"], "target_role": kwargs["target_role"],
            "status": "pending", "email_sent": False, "created_at": datetime(2026, 6, 12, tzinfo=tz.utc),
        }, True

    async def _send_email(_settings, **_kwargs):
        return False  # no Resend key in test

    async def _create_notif(_db, **kwargs):
        created_notifs.append(kwargs)
        return {"id": "n1", **kwargs, "read": False, "created_at": datetime(2026, 6, 12, tzinfo=timezone.utc)}

    monkeypatch.setattr("app.db.repositories.get_or_create_profile_from_claims", _profile)
    monkeypatch.setattr("app.db.repositories.create_social_request", _create_request)
    monkeypatch.setattr("app.services.email_service.send_email", _send_email)
    monkeypatch.setattr("app.db.repositories.create_notification", _create_notif)

    r = api_client.post("/v1/social/intro-request", json={"mentor_node_id": "mentor_priya_shah"})
    assert r.status_code == 200
    assert len(created_notifs) == 1
    assert created_notifs[0]["type"] == "intro_sent"
    assert created_notifs[0]["user_id"] == "p1"
