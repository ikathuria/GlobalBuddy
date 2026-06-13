"""Discovery feed tests: public browse over Markdown content, save auth gate."""

from __future__ import annotations


def test_feed_browse_is_public_and_returns_items(api_client) -> None:
    r = api_client.get("/v1/feed", params={"city": "Chicago"})
    assert r.status_code == 200
    data = r.json()
    assert data["items"]
    assert all(item["type"] in {"guide", "event", "food", "tip"} for item in data["items"])
    # Saved is always false without auth.
    assert all(item["saved"] is False for item in data["items"])


def test_feed_category_filter(api_client) -> None:
    r = api_client.get("/v1/feed", params={"city": "Chicago", "category": "guide"})
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    assert all(item["type"] == "guide" for item in items)


def test_feed_unknown_category_rejected(api_client) -> None:
    r = api_client.get("/v1/feed", params={"category": "bogus"})
    assert r.status_code == 422


def test_feed_pagination_offsets(api_client) -> None:
    first = api_client.get("/v1/feed", params={"city": "Chicago", "limit": 2, "offset": 0}).json()
    assert len(first["items"]) <= 2
    if first["next_offset"] is not None:
        second = api_client.get(
            "/v1/feed", params={"city": "Chicago", "limit": 2, "offset": first["next_offset"]}
        ).json()
        first_ids = {i["id"] for i in first["items"]}
        second_ids = {i["id"] for i in second["items"]}
        assert first_ids.isdisjoint(second_ids)


def test_feed_save_requires_auth(api_client) -> None:
    r = api_client.post("/v1/feed/save", json={"content_id": "guide_cta_ventra_basics"})
    assert r.status_code == 401


def test_feed_saved_requires_auth(api_client) -> None:
    r = api_client.get("/v1/feed/saved")
    assert r.status_code == 401
