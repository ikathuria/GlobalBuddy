"""Transactional email via Resend.

Graceful by design: when RESEND_API_KEY is absent the service logs the intent
and reports ``sent=False`` instead of raising, so intro requests still record in
Neon during local/demo runs without an email provider configured.
"""

from __future__ import annotations

import logging

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

_RESEND_ENDPOINT = "https://api.resend.com/emails"
_DEFAULT_FROM = "Globalदोस्त <onboarding@resend.dev>"


async def send_email(
    settings: Settings,
    *,
    to: str,
    subject: str,
    html: str,
    reply_to: str | None = None,
) -> bool:
    """Send one email. Returns True only when Resend accepted the request."""
    api_key = settings.resend_api_key.strip()
    if not api_key:
        logger.info("ai_event=email_skipped reason=no_resend_key to=%s subject=%s", to, subject)
        return False
    if not to.strip():
        logger.warning("ai_event=email_skipped reason=no_recipient subject=%s", subject)
        return False

    payload: dict[str, object] = {
        "from": _DEFAULT_FROM,
        "to": [to.strip()],
        "subject": subject,
        "html": html,
    }
    if reply_to:
        payload["reply_to"] = reply_to

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                _RESEND_ENDPOINT,
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
    except Exception as exc:  # noqa: BLE001 - email is best-effort, never fatal
        logger.warning("ai_event=email_failed to=%s subject=%s error=%s", to, subject, exc)
        return False

    if response.status_code >= 300:
        logger.warning(
            "ai_event=email_failed to=%s subject=%s http_status=%d body=%s",
            to, subject, response.status_code, response.text[:200],
        )
        return False

    logger.info("ai_event=email_sent to=%s subject=%s", to, subject)
    return True
