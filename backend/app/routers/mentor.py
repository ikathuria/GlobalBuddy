"""Mentor system (M13): opt-in, public directory, and ratings.

The directory merges Markdown seed mentors with opted-in Neon mentor profiles.
Opting in requires the user to already be a settler/local/mentor and is the only
path to the `mentor` stage (never automatic). Ratings apply to real (Neon)
mentors; seed mentors are read-only demo data.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.auth import require_principal
from app.db import repositories

router = APIRouter(prefix="/v1/mentors", tags=["mentors"])

ELIGIBLE_STAGES = {"settler", "local", "mentor"}


class MentorOptIn(BaseModel):
    expertise: list[str] = Field(default_factory=list)
    availability: str = "available"
    bio: str = ""


class AvailabilityUpdate(BaseModel):
    availability: str = Field(pattern="^(available|paused)$")


class MentorRating(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = ""


class MentorCardOut(BaseModel):
    id: str
    source: str
    name: str
    city: str = ""
    university: str = ""
    country: str = ""
    expertise: list[str] = Field(default_factory=list)
    bio: str = ""
    rating: float = 0.0
    availability: str = "available"
    can_rate: bool = False


class MentorDirectory(BaseModel):
    items: list[MentorCardOut]


def _require_db(request: Request):
    db = getattr(request.app.state, "db", None)
    if db is None or not db.enabled:
        raise HTTPException(status_code=503, detail="Postgres persistence is not configured.")
    return db


def _seed_mentors(request: Request) -> list[MentorCardOut]:
    graph_service = getattr(request.app.state, "graph_service", None)
    if getattr(graph_service, "source", "") != "markdown":
        return []
    cards: list[MentorCardOut] = []
    for node in graph_service.nodes_by_type("Mentor"):
        data = node.data
        expertise = [str(x) for x in (data.get("needs") or [])] + [str(x) for x in (data.get("languages") or [])]
        cards.append(
            MentorCardOut(
                id=node.id,
                source="seed",
                name=node.title,
                city=node.city,
                university=str(data.get("university") or ""),
                country=str(data.get("country_of_origin") or ""),
                expertise=expertise,
                bio=str(data.get("connect_hint") or ""),
                rating=float(data.get("trust_score") or 0.0) * 5.0,
                availability="available",
                can_rate=False,
            )
        )
    return cards


def _matches(card: MentorCardOut, *, city: str, university: str, country: str, expertise: str) -> bool:
    def has(haystack: str, needle: str) -> bool:
        return not needle or needle.lower() in (haystack or "").lower()

    if not has(card.city, city) or not has(card.university, university) or not has(card.country, country):
        return False
    if expertise and not any(expertise.lower() in e.lower() for e in card.expertise):
        return False
    return True


@router.get("", response_model=MentorDirectory)
async def list_mentors(
    request: Request,
    city: str = Query(default=""),
    university: str = Query(default=""),
    country: str = Query(default=""),
    expertise: str = Query(default=""),
) -> MentorDirectory:
    cards = _seed_mentors(request)

    db = getattr(request.app.state, "db", None)
    if db is not None and db.enabled:
        for row in await repositories.list_mentor_profiles(db):
            if str(row.get("availability") or "") == "paused":
                continue
            cards.append(
                MentorCardOut(
                    id=str(row["user_id"]),
                    source="neon",
                    name=str(row.get("full_name") or "Globalदोस्त mentor"),
                    city=str(row.get("target_city") or ""),
                    university=str(row.get("target_university") or ""),
                    country=str(row.get("country_of_origin") or ""),
                    expertise=[str(x) for x in (row.get("expertise") or [])],
                    bio=str(row.get("bio") or ""),
                    rating=float(row.get("rating") or 0.0),
                    availability=str(row.get("availability") or "available"),
                    can_rate=True,
                )
            )

    filtered = [c for c in cards if _matches(c, city=city, university=university, country=country, expertise=expertise)]
    filtered.sort(key=lambda c: c.rating, reverse=True)
    return MentorDirectory(items=filtered)


@router.get("/me")
async def get_my_mentor_profile(request: Request) -> dict:
    principal = require_principal(request)
    db = _require_db(request)
    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    mentor = await repositories.get_mentor_profile(db, user_id=str(profile["id"]))
    if mentor is None:
        return {"opted_in": False, "stage": str(profile.get("stage") or "newcomer")}
    return {
        "opted_in": True,
        "stage": str(profile.get("stage") or "mentor"),
        "expertise": list(mentor.get("expertise") or []),
        "availability": str(mentor.get("availability") or "available"),
        "bio": str(mentor.get("bio") or ""),
        "rating": float(mentor.get("rating") or 0.0),
        "intro_count": int(mentor.get("intro_count") or 0),
    }


@router.post("/opt-in")
async def opt_in(payload: MentorOptIn, request: Request) -> dict:
    principal = require_principal(request)
    db = _require_db(request)
    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    stage = str(profile.get("stage") or "newcomer")
    if stage not in ELIGIBLE_STAGES:
        raise HTTPException(status_code=403, detail="Become a settler before opting in as a mentor.")

    mentor = await repositories.opt_in_mentor(
        db,
        user_id=str(profile["id"]),
        expertise=payload.expertise,
        availability=payload.availability or "available",
        bio=payload.bio,
    )
    return {
        "opted_in": True,
        "stage": "mentor",
        "expertise": list(mentor.get("expertise") or []),
        "availability": str(mentor.get("availability") or "available"),
        "bio": str(mentor.get("bio") or ""),
    }


@router.patch("/me/availability")
async def update_availability(payload: AvailabilityUpdate, request: Request) -> dict:
    principal = require_principal(request)
    db = _require_db(request)
    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    row = await repositories.set_mentor_availability(db, user_id=str(profile["id"]), availability=payload.availability)
    if row is None:
        raise HTTPException(status_code=404, detail="You have not opted in as a mentor.")
    return {"availability": str(row.get("availability") or "available")}


@router.post("/{mentor_id}/rate")
async def rate_mentor(mentor_id: str, payload: MentorRating, request: Request) -> dict:
    principal = require_principal(request)
    db = _require_db(request)
    profile = await repositories.get_or_create_profile_from_claims(db, principal.claims)
    reviewer_id = str(profile["id"])
    if reviewer_id == mentor_id:
        raise HTTPException(status_code=400, detail="You cannot rate yourself.")

    mentor = await repositories.get_mentor_profile(db, user_id=mentor_id)
    if mentor is None:
        raise HTTPException(status_code=404, detail="Mentor not found.")

    new_avg = await repositories.add_mentor_rating(
        db,
        mentor_id=mentor_id,
        reviewer_id=reviewer_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    return {"mentor_id": mentor_id, "rating": new_avg}
