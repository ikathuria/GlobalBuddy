"""RocketRide-compatible HTTP inference — swap URL when your workspace exposes it."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings
from app.utils.json_tools import extract_json_object

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = httpx.Timeout(15.0, read=120.0)


class HttpRocketRideProvider:
    name = "rocketride_http"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate_plan(
        self,
        evidence_bundle: dict[str, Any],
        student_profile: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return await self._post(
            system_prompt=(
                "Return JSON plan grounded in evidence_bundle only; cite names only from bundle lists "
                "(mentors, peers, restaurants, events, resources, places_of_worship, grocery_stores, "
                "housing_areas, exploration_spots, transit_tips). No invented routes or live schedules."
            ),
            user_payload={"student_profile": student_profile, "evidence_bundle": evidence_bundle},
            schema_hint='{"plan_title":"","best_next_action":"","steps":[],"priority_contacts":[],"warnings":[],"confidence":0}',
        )

    async def explain_term(
        self,
        term: str,
        home_country: str,
        context: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        return await self._post(
            system_prompt="Cultural bridge JSON only.",
            user_payload={"term": term, "home_country": home_country, "context": context},
            schema_hint='{"plain_explanation":"","home_context_analogy":"","common_mistakes":[],"what_to_do_next":[]}',
        )

    async def _post(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema_hint: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        url = self._settings.rocketride_http_completion_url.strip()
        body = {
            "system": system_prompt,
            "user": user_payload,
            "response_format": "json_object",
            "schema": schema_hint,
        }
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            response = await client.post(
                url,
                json=body,
                headers={
                    "Authorization": f"Bearer {self._settings.rocketride_apikey}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()
        parsed = data.get("output") or data.get("result") or data.get("json") or data
        if isinstance(parsed, str):
            parsed_obj = extract_json_object(parsed) or {}
        else:
            parsed_obj = parsed if isinstance(parsed, dict) else {}
        return parsed_obj, {"provider": self.name, "status": response.status_code}
