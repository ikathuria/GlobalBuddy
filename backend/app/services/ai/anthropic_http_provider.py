"""Anthropic Messages API via httpx — optional fallback."""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import Settings
from app.utils.json_tools import extract_json_object

_HTTP_TIMEOUT = httpx.Timeout(15.0, read=120.0)


class AnthropicHttpProvider:
    name = "anthropic_httpx"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate_plan(
        self,
        evidence_bundle: dict[str, Any],
        student_profile: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        system = "Return JSON only. Ground in evidence_bundle. Include best_next_action."
        user_text = json.dumps(
            {"student_profile": student_profile, "evidence_bundle": evidence_bundle},
            ensure_ascii=False,
        )
        return await self._messages(system, user_text)

    async def explain_term(
        self,
        term: str,
        home_country: str,
        context: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        system = "Return JSON only for cultural bridge."
        user_text = json.dumps({"term": term, "home_country": home_country, "context": context})
        return await self._messages(system, user_text)

    async def _messages(self, system: str, user_text: str) -> tuple[dict[str, Any], dict[str, Any]]:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self._settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,
                    "system": system,
                    "messages": [{"role": "user", "content": user_text}],
                },
            )
            response.raise_for_status()
            payload = response.json()
        text_blocks = []
        for block in payload.get("content", []) or []:
            if block.get("type") == "text":
                text_blocks.append(block.get("text", ""))
        combined = "\n".join(text_blocks)
        parsed = extract_json_object(combined) or {}
        return parsed, {"provider": self.name, "status": response.status_code}
