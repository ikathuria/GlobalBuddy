"""Resolve AI provider from settings — priority: explicit AI_PROVIDER > Gemini > RocketRide SDK > RocketRide HTTP > Anthropic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.config import Settings
from app.services.ai.anthropic_http_provider import AnthropicHttpProvider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.http_rocketride_provider import HttpRocketRideProvider
from app.services.ai.rocketride_sdk_provider import RocketRideSdkProvider

if TYPE_CHECKING:
    from app.services.ai.protocol import AIProvider

logger = logging.getLogger(__name__)


def get_ai_provider(settings: Settings) -> "AIProvider":
    mode = (settings.ai_provider or "auto").strip().lower()

    if mode == "gemini" or (mode == "auto" and settings.gemini_api_key.strip()):
        if not settings.gemini_api_key.strip():
            raise ValueError("AI_PROVIDER=gemini requires GEMINI_API_KEY")
        return GeminiProvider(settings)

    if mode == "rocketride_sdk" or (
        mode == "auto"
        and settings.rocketride_uri.strip()
        and settings.rocketride_apikey.strip()
    ):
        if not settings.rocketride_uri.strip():
            raise ValueError("rocketride_sdk requires ROCKETRIDE_URI")
        return RocketRideSdkProvider(settings)

    if mode == "rocketride_http" or (
        mode == "auto"
        and settings.rocketride_http_completion_url.strip()
        and settings.rocketride_apikey.strip()
    ):
        if not settings.rocketride_http_completion_url.strip():
            raise ValueError("rocketride_http requires ROCKETRIDE_HTTP_COMPLETION_URL")
        return HttpRocketRideProvider(settings)

    if mode == "anthropic" or (mode == "auto" and settings.anthropic_api_key.strip()):
        if not settings.anthropic_api_key.strip():
            raise ValueError("anthropic provider requires ANTHROPIC_API_KEY")
        return AnthropicHttpProvider(settings)

    raise ValueError(
        "No AI provider configured. Set GEMINI_API_KEY (+ optional AI_PROVIDER=gemini), "
        "or ROCKETRIDE_URI + ROCKETRIDE_APIKEY, "
        "or ROCKETRIDE_HTTP_COMPLETION_URL + ROCKETRIDE_APIKEY, "
        "or ANTHROPIC_API_KEY."
    )
