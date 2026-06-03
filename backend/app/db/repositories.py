"""Repository helpers for Neon Postgres app data."""

from __future__ import annotations

import json
from typing import Any

from app.db.postgres import PostgresDatabase
from app.models.schemas import ProfileMatchRequest


def _claim_value(claims: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = claims.get(key)
        if value:
            return str(value)
    return ""


async def get_or_create_user_profile(
    db: PostgresDatabase,
    *,
    auth_user_id: str,
    email: str = "",
    full_name: str = "",
) -> dict[str, Any]:
    row = await db.fetchrow(
        """
        insert into user_profiles (auth_user_id, email, full_name)
        values ($1, $2, $3)
        on conflict (auth_user_id) do update
          set email = coalesce(nullif(excluded.email, ''), user_profiles.email),
              full_name = coalesce(nullif(excluded.full_name, ''), user_profiles.full_name)
        returning *
        """,
        auth_user_id,
        email,
        full_name,
    )
    if row is None:
        raise RuntimeError("Unable to resolve user profile.")
    return row


async def get_or_create_profile_from_claims(db: PostgresDatabase, claims: dict[str, Any]) -> dict[str, Any]:
    auth_user_id = _claim_value(claims, "sub", "id", "user_id")
    if not auth_user_id:
        raise RuntimeError("JWT did not include a user id claim.")
    email = _claim_value(claims, "email")
    full_name = _claim_value(claims, "name", "full_name")
    return await get_or_create_user_profile(db, auth_user_id=auth_user_id, email=email, full_name=full_name)


async def update_profile_from_match(
    db: PostgresDatabase,
    *,
    auth_user_id: str,
    payload: ProfileMatchRequest,
) -> dict[str, Any]:
    row = await db.fetchrow(
        """
        insert into user_profiles (
          auth_user_id, full_name, email, country_of_origin, target_university, target_city
        )
        values ($1, $2, $3, $4, $5, $6)
        on conflict (auth_user_id) do update
          set full_name = excluded.full_name,
              email = excluded.email,
              country_of_origin = excluded.country_of_origin,
              target_university = excluded.target_university,
              target_city = excluded.target_city
        returning *
        """,
        auth_user_id,
        payload.full_name.strip(),
        payload.email.strip(),
        payload.country_of_origin.strip(),
        payload.target_university.strip(),
        payload.target_city.strip(),
    )
    if row is None:
        raise RuntimeError("Unable to persist user profile.")
    return row


async def list_plan_progress(db: PostgresDatabase, *, user_id: str) -> list[dict[str, Any]]:
    return await db.fetch(
        """
        select task_id, completed, updated_at
        from plan_progress
        where user_id = $1
        order by updated_at desc
        """,
        user_id,
    )


async def set_plan_progress(
    db: PostgresDatabase,
    *,
    user_id: str,
    task_id: str,
    completed: bool,
) -> dict[str, Any]:
    row = await db.fetchrow(
        """
        insert into plan_progress (user_id, task_id, completed, updated_at)
        values ($1, $2, $3, now())
        on conflict (user_id, task_id) do update
          set completed = excluded.completed,
              updated_at = now()
        returning task_id, completed, updated_at
        """,
        user_id,
        task_id,
        completed,
    )
    if row is None:
        raise RuntimeError("Unable to persist plan progress.")
    return row


async def add_chat_message(
    db: PostgresDatabase,
    *,
    user_id: str,
    session_id: str,
    role: str,
    content: str,
) -> dict[str, Any]:
    row = await db.fetchrow(
        """
        insert into chat_messages (user_id, session_id, role, content)
        values ($1, $2, $3, $4)
        returning id, role, content, created_at
        """,
        user_id,
        session_id,
        role,
        content,
    )
    if row is None:
        raise RuntimeError("Unable to persist chat message.")
    return row


async def list_chat_messages(
    db: PostgresDatabase,
    *,
    user_id: str,
    session_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return await db.fetch(
        """
        select role, content
        from (
          select role, content, created_at
          from chat_messages
          where user_id = $1 and session_id = $2
          order by created_at desc
          limit $3
        ) recent
        order by created_at asc
        """,
        user_id,
        session_id,
        limit,
    )


async def list_user_documents(db: PostgresDatabase, *, user_id: str) -> list[dict[str, Any]]:
    return await db.fetch(
        """
        select doc_type, status, updated_at
        from user_documents
        where user_id = $1
        order by updated_at desc
        """,
        user_id,
    )


async def set_user_document_status(
    db: PostgresDatabase,
    *,
    user_id: str,
    doc_type: str,
    status: str,
) -> dict[str, Any]:
    row = await db.fetchrow(
        """
        insert into user_documents (user_id, doc_type, status, updated_at)
        values ($1, $2, $3, now())
        on conflict (user_id, doc_type) do update
          set status = excluded.status,
              updated_at = now()
        returning doc_type, status, updated_at
        """,
        user_id,
        doc_type,
        status,
    )
    if row is None:
        raise RuntimeError("Unable to persist document status.")
    return row


async def set_app_session(
    db: PostgresDatabase,
    *,
    session_id: str,
    payload: dict[str, Any],
    ttl_hours: int = 24,
) -> dict[str, Any]:
    row = await db.fetchrow(
        """
        insert into app_sessions (session_id, payload, expires_at, updated_at)
        values ($1, $2::jsonb, now() + ($3::text || ' hours')::interval, now())
        on conflict (session_id) do update
          set payload = excluded.payload,
              expires_at = excluded.expires_at,
              updated_at = now()
        returning session_id, payload, expires_at
        """,
        session_id,
        json.dumps(payload),
        ttl_hours,
    )
    if row is None:
        raise RuntimeError("Unable to persist app session.")
    return row


async def get_app_session(db: PostgresDatabase, *, session_id: str) -> dict[str, Any] | None:
    await db.execute("delete from app_sessions where expires_at <= now()")
    row = await db.fetchrow(
        """
        select payload
        from app_sessions
        where session_id = $1 and expires_at > now()
        """,
        session_id,
    )
    if row is None:
        return None
    payload = row.get("payload")
    if isinstance(payload, str):
        payload = json.loads(payload)
    return dict(payload) if isinstance(payload, dict) else None


async def update_app_session(
    db: PostgresDatabase,
    *,
    session_id: str,
    ttl_hours: int = 24,
    **fields: Any,
) -> dict[str, Any] | None:
    current = await get_app_session(db, session_id=session_id) or {}
    current.update(fields)
    return await set_app_session(db, session_id=session_id, payload=current, ttl_hours=ttl_hours)
