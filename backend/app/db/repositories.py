"""Repository helpers for Neon Postgres app data."""

from __future__ import annotations

import json
from typing import Any

from app.db.postgres import PostgresDatabase
from app.models.schemas import ProfileMatchRequest
from app.utils.stages import infer_user_stage, normalize_stage, parse_arrival_date


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
    arrival_date = parse_arrival_date(payload.arrival_date)
    inferred_stage = infer_user_stage(arrival_date)
    row = await db.fetchrow(
        """
        insert into user_profiles (
          auth_user_id, full_name, email, country_of_origin, target_university, target_city, stage, arrival_date
        )
        values ($1, $2, $3, $4, $5, $6, $7, $8)
        on conflict (auth_user_id) do update
          set full_name = excluded.full_name,
              email = excluded.email,
              country_of_origin = excluded.country_of_origin,
              target_university = excluded.target_university,
              target_city = excluded.target_city,
              arrival_date = coalesce(excluded.arrival_date, user_profiles.arrival_date),
              stage = case
                when case user_profiles.stage
                  when 'newcomer' then 0
                  when 'settler' then 1
                  when 'local' then 2
                  when 'mentor' then 3
                  else 0
                end >= case excluded.stage
                  when 'newcomer' then 0
                  when 'settler' then 1
                  when 'local' then 2
                  when 'mentor' then 3
                  else 0
                end then user_profiles.stage
                else excluded.stage
              end
        returning *
        """,
        auth_user_id,
        payload.full_name.strip(),
        payload.email.strip(),
        payload.country_of_origin.strip(),
        payload.target_university.strip(),
        payload.target_city.strip(),
        inferred_stage,
        arrival_date,
    )
    if row is None:
        raise RuntimeError("Unable to persist user profile.")
    return row


async def advance_user_stage(
    db: PostgresDatabase,
    *,
    auth_user_id: str,
    stage: str,
) -> dict[str, Any]:
    target_stage = normalize_stage(stage, allow_mentor=False)
    if target_stage is None:
        raise ValueError("Invalid stage.")
    row = await db.fetchrow(
        """
        update user_profiles
        set stage = case
          when case $2
            when 'newcomer' then 0
            when 'settler' then 1
            when 'local' then 2
            else 0
          end > case stage
            when 'newcomer' then 0
            when 'settler' then 1
            when 'local' then 2
            when 'mentor' then 3
            else 0
          end then $2
          else stage
        end
        where auth_user_id = $1
        returning *
        """,
        auth_user_id,
        target_stage,
    )
    if row is None:
        raise RuntimeError("Unable to update user stage.")
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


async def create_social_request(
    db: PostgresDatabase,
    *,
    requester_id: str,
    kind: str,
    target_node_id: str,
    target_name: str = "",
    target_role: str = "",
    message: str = "",
) -> tuple[dict[str, Any], bool]:
    """Insert a connection/intro request, idempotent per (requester, kind, target).

    Returns (row, created) where created is False when a prior request existed.
    """
    existing = await db.fetchrow(
        """
        select id, kind, target_node_id, target_name, target_role, status, email_sent, created_at
        from social_requests
        where requester_id = $1 and kind = $2 and target_node_id = $3
        """,
        requester_id,
        kind,
        target_node_id,
    )
    if existing is not None:
        return existing, False

    row = await db.fetchrow(
        """
        insert into social_requests (requester_id, kind, target_node_id, target_name, target_role, message)
        values ($1, $2, $3, $4, $5, $6)
        returning id, kind, target_node_id, target_name, target_role, status, email_sent, created_at
        """,
        requester_id,
        kind,
        target_node_id,
        target_name,
        target_role,
        message,
    )
    if row is None:
        raise RuntimeError("Unable to persist social request.")
    return row, True


async def mark_social_request_email_sent(
    db: PostgresDatabase,
    *,
    request_id: str,
) -> None:
    await db.execute("update social_requests set email_sent = true where id = $1", request_id)


async def list_social_requests(db: PostgresDatabase, *, requester_id: str) -> list[dict[str, Any]]:
    return await db.fetch(
        """
        select id, kind, target_node_id, target_name, target_role, status, email_sent, created_at
        from social_requests
        where requester_id = $1
        order by created_at desc
        """,
        requester_id,
    )


async def opt_in_mentor(
    db: PostgresDatabase,
    *,
    user_id: str,
    expertise: list[str],
    availability: str,
    bio: str,
) -> dict[str, Any]:
    row = await db.fetchrow(
        """
        insert into mentor_profiles (user_id, expertise, availability, bio)
        values ($1, $2, $3, $4)
        on conflict (user_id) do update
          set expertise = excluded.expertise,
              availability = excluded.availability,
              bio = excluded.bio
        returning user_id, expertise, availability, bio, response_rate, intro_count, rating, opted_in_at
        """,
        user_id,
        expertise,
        availability,
        bio,
    )
    if row is None:
        raise RuntimeError("Unable to persist mentor profile.")
    # Opting in is the explicit, non-automatic path to the mentor stage.
    await db.execute("update user_profiles set stage = 'mentor' where id = $1", user_id)
    return row


async def set_mentor_availability(db: PostgresDatabase, *, user_id: str, availability: str) -> dict[str, Any] | None:
    return await db.fetchrow(
        """
        update mentor_profiles set availability = $2 where user_id = $1
        returning user_id, expertise, availability, bio, response_rate, intro_count, rating, opted_in_at
        """,
        user_id,
        availability,
    )


async def get_mentor_profile(db: PostgresDatabase, *, user_id: str) -> dict[str, Any] | None:
    return await db.fetchrow(
        """
        select user_id, expertise, availability, bio, response_rate, intro_count, rating, opted_in_at
        from mentor_profiles where user_id = $1
        """,
        user_id,
    )


async def list_mentor_profiles(db: PostgresDatabase) -> list[dict[str, Any]]:
    """Opted-in mentors joined with their public profile fields."""
    return await db.fetch(
        """
        select
          mp.user_id, mp.expertise, mp.availability, mp.bio, mp.rating, mp.intro_count,
          up.full_name, up.country_of_origin, up.target_university, up.target_city
        from mentor_profiles mp
        join user_profiles up on up.id = mp.user_id
        order by mp.rating desc, mp.intro_count desc
        """
    )


async def add_mentor_rating(
    db: PostgresDatabase,
    *,
    mentor_id: str,
    reviewer_id: str,
    rating: int,
    comment: str = "",
) -> float:
    """Upsert a rating and recompute the mentor's average. Returns the new average."""
    await db.execute(
        """
        insert into mentor_ratings (mentor_id, reviewer_id, rating, comment)
        values ($1, $2, $3, $4)
        on conflict (mentor_id, reviewer_id) do update
          set rating = excluded.rating, comment = excluded.comment
        """,
        mentor_id,
        reviewer_id,
        rating,
        comment,
    )
    row = await db.fetchrow(
        "select coalesce(avg(rating), 0)::float as avg from mentor_ratings where mentor_id = $1",
        mentor_id,
    )
    new_avg = float(row["avg"]) if row else 0.0
    await db.execute("update mentor_profiles set rating = $2 where user_id = $1", mentor_id, new_avg)
    return round(new_avg, 2)


async def list_content_items(
    db: PostgresDatabase,
    *,
    city: str = "",
    content_type: str = "",
) -> list[dict[str, Any]]:
    return await db.fetch(
        """
        select id, type, title, body, city, tags, published_at, created_at
        from content_items
        where published_at is not null
          and ($1 = '' or lower(city) = lower($1))
          and ($2 = '' or type = $2)
        order by coalesce(published_at, created_at) desc
        """,
        city,
        content_type,
    )


async def add_saved_content(
    db: PostgresDatabase,
    *,
    user_id: str,
    content_id: str,
    content_source: str = "markdown",
) -> None:
    await db.execute(
        """
        insert into saved_content (user_id, content_id, content_source)
        values ($1, $2, $3)
        on conflict (user_id, content_id, content_source) do nothing
        """,
        user_id,
        content_id,
        content_source,
    )


async def remove_saved_content(
    db: PostgresDatabase,
    *,
    user_id: str,
    content_id: str,
    content_source: str = "markdown",
) -> None:
    await db.execute(
        "delete from saved_content where user_id = $1 and content_id = $2 and content_source = $3",
        user_id,
        content_id,
        content_source,
    )


async def list_saved_content(db: PostgresDatabase, *, user_id: str) -> list[dict[str, Any]]:
    return await db.fetch(
        """
        select content_id, content_source, created_at
        from saved_content
        where user_id = $1
        order by created_at desc
        """,
        user_id,
    )


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
