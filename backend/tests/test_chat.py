"""Chat endpoint tests: /v1/chat/message and the SSE /v1/chat/stream variant."""

from __future__ import annotations

import json

import pytest


class _StreamingProvider:
    name = "stream-mock"

    async def chat_reply(self, history: list, message: str) -> str:
        return "full reply"

    async def chat_reply_stream(self, history: list, message: str):
        for chunk in ["Hello", " international", " student!"]:
            yield chunk


class _NonStreamingProvider:
    name = "plain-mock"

    async def chat_reply(self, history: list, message: str) -> str:
        return "plain reply"


class _BrokenStreamProvider:
    name = "broken-mock"

    async def chat_reply_stream(self, history: list, message: str):
        yield "partial"
        raise RuntimeError("provider exploded")


def _sse_events(body: str) -> list[dict]:
    events = []
    for block in body.split("\n\n"):
        for line in block.split("\n"):
            if line.startswith("data: "):
                events.append(json.loads(line[len("data: "):]))
    return events


def test_chat_message_returns_reply(api_client: object, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agents.chat_agent.get_ai_provider", lambda _: _NonStreamingProvider())

    r = api_client.post("/v1/chat/message", json={"message": "What is an SSN?"})

    assert r.status_code == 200
    data = r.json()
    assert data["reply"] == "plain reply"
    assert data["session_id"]
    assert data["fallback_used"] is False


def test_chat_stream_yields_session_deltas_and_done(api_client: object, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agents.chat_agent.get_ai_provider", lambda _: _StreamingProvider())

    r = api_client.post("/v1/chat/stream", json={"message": "What is an SSN?"})

    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    events = _sse_events(r.text)
    assert events[0]["type"] == "session"
    deltas = [e["text"] for e in events if e["type"] == "delta"]
    assert deltas == ["Hello", " international", " student!"]
    done = events[-1]
    assert done["type"] == "done"
    assert done["reply"] == "Hello international student!"
    assert done["fallback_used"] is False
    assert done["session_id"] == events[0]["session_id"]


def test_chat_stream_falls_back_to_single_delta_without_stream_support(
    api_client: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.agents.chat_agent.get_ai_provider", lambda _: _NonStreamingProvider())

    r = api_client.post("/v1/chat/stream", json={"message": "What is an SSN?"})

    assert r.status_code == 200
    events = _sse_events(r.text)
    deltas = [e["text"] for e in events if e["type"] == "delta"]
    assert deltas == ["plain reply"]
    assert events[-1]["type"] == "done"
    assert events[-1]["fallback_used"] is False


def test_chat_stream_keeps_partial_reply_when_provider_fails(
    api_client: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.agents.chat_agent.get_ai_provider", lambda _: _BrokenStreamProvider())

    r = api_client.post("/v1/chat/stream", json={"message": "What is an SSN?"})

    assert r.status_code == 200
    events = _sse_events(r.text)
    done = events[-1]
    assert done["type"] == "done"
    assert done["reply"] == "partial"
    assert done["fallback_used"] is True


def test_chat_stream_continues_session_history(api_client: object, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agents.chat_agent.get_ai_provider", lambda _: _StreamingProvider())

    first = api_client.post("/v1/chat/stream", json={"message": "first question"})
    sid = _sse_events(first.text)[0]["session_id"]

    second = api_client.post("/v1/chat/stream", json={"message": "second question", "session_id": sid})
    events = _sse_events(second.text)
    assert events[0]["session_id"] == sid

    history = api_client.get(f"/v1/chat/history/{sid}").json()
    roles = [m["role"] for m in history["messages"]]
    assert roles == ["user", "assistant", "user", "assistant"]
