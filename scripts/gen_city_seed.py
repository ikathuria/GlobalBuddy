"""Generate Boston and NYC Markdown graph nodes (M15 multi-city expansion).

Mirrors the structure of the hand-authored Chicago graph. Data is representative
demo content; ids are city-prefixed to stay globally unique. Run:

    python scripts/gen_city_seed.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1] / "data" / "graph"


def _write(city_dir: str, subdir: str, slug: str, frontmatter: dict, body: str) -> None:
    path = ROOT / city_dir / subdir / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    path.write_text(f"---\n{fm}\n---\n\n# {frontmatter['title']}\n\n{body}\n", encoding="utf-8", newline="\n")


# city key -> (folder, display name, universities[(id,title,uni_tags)], data...)
CITIES = {
    "boston": {
        "name": "Boston",
        "universities": [
            ("univ_neu", "Northeastern University", ["Northeastern University", "Northeastern", "NEU"]),
            ("univ_bu", "Boston University", ["Boston University", "BU"]),
            ("univ_mit", "Massachusetts Institute of Technology", ["MIT", "Massachusetts Institute of Technology"]),
        ],
        "mentors": [
            ("priya_venkataraman", "Priya Venkataraman", "India", ["India", "IN"], "Northeastern University", ["Northeastern", "NEU"], ["banking", "housing"], 0.91, ["English", "Tamil", "Hindi"], "Mention Globalदोस्त and Northeastern ISS in your message."),
            ("ali_hassan", "Ali Hassan", "Pakistan", ["Pakistan", "PK"], "Boston University", ["BU"], ["housing", "community"], 0.88, ["English", "Urdu"], "Coffee near BU campus — say you matched on Globalदोस्त."),
            ("wei_chen", "Wei Chen", "China", ["China", "CN"], "Massachusetts Institute of Technology", ["MIT"], ["banking", "employment"], 0.9, ["English", "Mandarin"], "Best reached about research-assistant and CPT questions."),
            ("ananya_rao", "Ananya Rao", "India", ["India", "IN"], "Boston University", ["BU"], ["community", "housing"], 0.86, ["English", "Telugu", "Hindi"], "Happy to share Allston apartment-hunting tips."),
            ("diego_morales", "Diego Morales", "Mexico", ["Mexico", "MX"], "Northeastern University", ["Northeastern", "NEU"], ["employment", "banking"], 0.84, ["English", "Spanish"], "Ask about co-op placements and first US job search."),
        ],
        "peers": [
            ("sana_iqbal", "Sana Iqbal", "Boston University", ["BU"], "Allston-Brighton"),
            ("ravi_kumar", "Ravi Kumar", "Northeastern University", ["Northeastern", "NEU"], "Fenway-Kenmore"),
        ],
        "worship": [
            ("sri_lakshmi_temple", "Sri Lakshmi Temple", "Hindu temple", "Ashland", 42.2526, -71.4953, ["hindu", "indian", "south_asian"]),
            ("isboston_masjid", "Islamic Society of Boston", "Mosque", "Cambridge", 42.3637, -71.1037, ["muslim", "halal"]),
        ],
        "grocery": [
            ("patel_brothers_shrewsbury", "Patel Brothers (Shrewsbury)", "South Asian grocery", "Shrewsbury", 42.2706, -71.7137, ["indian", "south_asian", "vegetarian"]),
            ("hmart_cambridge", "H Mart (Cambridge)", "Asian grocery", "Cambridge", 42.3654, -71.1043, ["asian", "chinese", "korean"]),
        ],
        "housing": [
            ("allston_housing", "Allston-Brighton", "Student housing area", "Allston-Brighton", 42.3539, -71.1337, ["student", "affordable"]),
            ("mission_hill_housing", "Mission Hill", "Student housing area", "Mission Hill", 42.3329, -71.1029, ["student", "near_neu"]),
            ("cambridge_housing", "Cambridge (near MIT)", "Student housing area", "Cambridge", 42.3601, -71.0942, ["student", "near_mit"]),
        ],
        "exploration": [
            ("boston_common", "Boston Common", "Park", "Downtown", 42.3550, -71.0656, ["outdoors", "free"]),
            ("museum_fine_arts", "Museum of Fine Arts", "Museum", "Fenway", 42.3394, -71.0940, ["culture", "student_discount"]),
        ],
        "restaurants": [
            ("dosa_n_curry", "Dosa N Curry", 2, 3.1, ["India", "IN"], ["vegetarian"]),
            ("shan_a_punjab", "Shan-a-Punjab", 2, 4.0, ["India", "Pakistan", "IN"], ["halal"]),
        ],
        "resources": [
            ("neu_oglobal", "Northeastern OGS (International Student Services)", "university_support", ["documents", "employment"]),
            ("boston_newcomer_center", "Boston Newcomer Support Center", "community_support", ["housing", "community"]),
        ],
        "events": [
            ("neu_intl_orientation", "Northeastern International Orientation", "2026-08-25", "Curry Student Center", "orientation", ["India", "China", "US"]),
            ("diwali_boston", "Boston Diwali Celebration", "2026-10-30", "Back Bay", "cultural", ["India", "IN"]),
        ],
        "groups": [
            ("boston_desi_students", "Boston Desi Students", "WhatsApp", ["India", "IN"], []),
            ("neu_intl_telegram", "Northeastern International (Telegram)", "Telegram", [], ["Northeastern", "NEU"]),
        ],
        "guides": [
            ("boston_winter", "Surviving a Boston winter", "tip", ["weather", "boston", "newcomer"], "Boston winters bring nor'easters and ice. Get a heavy coat and waterproof boots, and learn the MBTA delays during storms."),
            ("mbta_charliecard", "Getting around on the MBTA CharlieCard", "tip", ["transit", "boston", "newcomer"], "The MBTA runs the 'T' subway and buses. Get a CharlieCard, and check whether your university offers a semester pass."),
        ],
        "tasks": [
            ("bos_iss_checkin", "Check in with your Boston ISS office", "university", "first_week", "critical", "Day 1-3", []),
            ("bos_open_bank", "Open a US bank account in Boston", "banking", "first_week", "high", "Day 3-7", ["task_bos_iss_checkin"]),
        ],
    },
    "nyc": {
        "name": "New York",
        "universities": [
            ("univ_nyu", "New York University", ["NYU", "New York University"]),
            ("univ_columbia", "Columbia University", ["Columbia", "Columbia University"]),
            ("univ_cuny", "City University of New York", ["CUNY", "City University of New York"]),
        ],
        "mentors": [
            ("meera_nair", "Meera Nair", "India", ["India", "IN"], "New York University", ["NYU"], ["housing", "banking"], 0.92, ["English", "Malayalam", "Hindi"], "Ask about Manhattan vs. Jersey City housing tradeoffs."),
            ("yusuf_demir", "Yusuf Demir", "Turkey", ["Turkey", "TR"], "Columbia University", ["Columbia"], ["community", "employment"], 0.89, ["English", "Turkish"], "Happy to talk OPT timelines and Morningside Heights life."),
            ("ling_zhao", "Ling Zhao", "China", ["China", "CN"], "Columbia University", ["Columbia"], ["banking", "employment"], 0.9, ["English", "Mandarin"], "Mention Globalदोस्त — I help with SSN and first job."),
            ("aisha_khan", "Aisha Khan", "Pakistan", ["Pakistan", "PK"], "City University of New York", ["CUNY"], ["housing", "community"], 0.85, ["English", "Urdu"], "Queens housing and halal food guide on request."),
            ("rahul_desai", "Rahul Desai", "India", ["India", "IN"], "New York University", ["NYU"], ["employment", "community"], 0.87, ["English", "Gujarati", "Hindi"], "Ask about tech internships and networking in NYC."),
        ],
        "peers": [
            ("nisha_patel", "Nisha Patel", "New York University", ["NYU"], "Jersey City"),
            ("chen_li", "Chen Li", "Columbia University", ["Columbia"], "Morningside Heights"),
        ],
        "worship": [
            ("ganesh_temple_flushing", "Hindu Temple Society (Flushing)", "Hindu temple", "Flushing", 40.7536, -73.8198, ["hindu", "indian", "south_asian"]),
            ("islamic_cultural_center", "Islamic Cultural Center of NY", "Mosque", "Upper East Side", 40.7918, -73.9510, ["muslim", "halal"]),
        ],
        "grocery": [
            ("patel_brothers_jackson_heights", "Patel Brothers (Jackson Heights)", "South Asian grocery", "Jackson Heights", 40.7488, -73.8917, ["indian", "south_asian", "vegetarian"]),
            ("hmart_ktown", "H Mart (Koreatown)", "Asian grocery", "Koreatown", 40.7475, -73.9866, ["asian", "korean", "chinese"]),
        ],
        "housing": [
            ("jersey_city_housing", "Jersey City", "Student housing area", "Jersey City", 40.7178, -74.0431, ["student", "affordable", "near_nyu"]),
            ("morningside_housing", "Morningside Heights", "Student housing area", "Morningside Heights", 40.8089, -73.9626, ["student", "near_columbia"]),
            ("astoria_housing", "Astoria", "Student housing area", "Astoria", 40.7644, -73.9235, ["student", "affordable"]),
        ],
        "exploration": [
            ("central_park", "Central Park", "Park", "Manhattan", 40.7829, -73.9654, ["outdoors", "free"]),
            ("met_museum", "The Met", "Museum", "Upper East Side", 40.7794, -73.9632, ["culture", "pay_what_you_wish"]),
        ],
        "restaurants": [
            ("saravanaa_bhavan", "Saravanaa Bhavan", 2, 2.0, ["India", "IN"], ["vegetarian"]),
            ("the_halal_guys", "The Halal Guys", 1, 1.2, ["Egypt", "US"], ["halal"]),
        ],
        "resources": [
            ("nyu_ogs", "NYU Office of Global Services", "university_support", ["documents", "employment"]),
            ("nyc_mayors_office_immigrant", "NYC Mayor's Office of Immigrant Affairs", "government_support", ["documents", "community"]),
        ],
        "events": [
            ("nyu_intl_orientation", "NYU International Student Orientation", "2026-08-26", "Kimmel Center", "orientation", ["India", "China", "US"]),
            ("diwali_nyc", "Diwali at South Street Seaport", "2026-10-29", "South Street Seaport", "cultural", ["India", "IN"]),
        ],
        "groups": [
            ("nyc_desi_students", "NYC Desi Students", "WhatsApp", ["India", "IN"], []),
            ("columbia_intl_telegram", "Columbia International (Telegram)", "Telegram", [], ["Columbia"]),
        ],
        "guides": [
            ("nyc_subway_omny", "Riding the NYC subway with OMNY", "tip", ["transit", "nyc", "newcomer"], "Tap to ride with OMNY (contactless card or phone) or get a MetroCard. Weekly fare-capping means you stop paying after enough rides."),
            ("nyc_first_apartment", "Renting your first NYC apartment", "tip", ["housing", "nyc", "newcomer"], "Expect broker fees, first/last month, and a security deposit. Guarantor services help international students without US credit."),
        ],
        "tasks": [
            ("nyc_iss_checkin", "Check in with your NYC ISS office", "university", "first_week", "critical", "Day 1-3", []),
            ("nyc_open_bank", "Open a US bank account in NYC", "banking", "first_week", "high", "Day 3-7", ["task_nyc_iss_checkin"]),
        ],
    },
}


def gen_city(key: str, spec: dict) -> int:
    city = spec["name"]
    folder = key
    count = 0

    _write(folder, "cities", key, {"id": f"city_{key}", "type": "City", "title": city, "city": city}, f"{city} city node for the Globalदोस्त graph.")
    count += 1

    for uid, title, tags in spec["universities"]:
        _write(folder, "universities", uid.replace("univ_", ""), {"id": uid, "type": "University", "title": title, "city": city, "aliases": tags}, f"{title} in {city}.")
        count += 1

    for slug, name, country, ctags, uni, utags, needs, trust, langs, hint in spec["mentors"]:
        _write(folder, "mentors", slug, {
            "id": f"mentor_{key}_{slug}", "type": "Mentor", "title": name, "city": city,
            "country_of_origin": country, "country_tags": ctags, "university": uni, "university_tags": utags,
            "needs": needs, "trust_score": trust, "languages": langs,
            "email": f"{slug}.{key}@globaldost.demo", "connect_hint": hint,
        }, f"{name} is a settled mentor connected to {uni}. Verify details before reaching out.")
        count += 1

    for slug, name, uni, utags, hood in spec["peers"]:
        _write(folder, "peers", slug, {
            "id": f"peer_{key}_{slug}", "type": "Peer", "title": name, "city": city,
            "university": uni, "university_tags": utags, "neighborhood": hood,
            "email": f"{slug}.{key}@globaldost.demo", "connect_hint": "Matched on destination; say hi via Globalदोस्त.",
        }, f"{name} is a peer near {uni}.")
        count += 1

    place_groups = [("PlaceOfWorship", "places", "worship"), ("GroceryStore", "places", "grocery"),
                    ("HousingArea", "places", "housing"), ("ExplorationSpot", "places", "exploration")]
    for node_type, subdir, field in place_groups:
        for slug, name, subtype, hood, lat, lon, atags in spec[field]:
            _write(folder, subdir, f"{key}-{slug}", {
                "id": f"place_{key}_{slug}", "type": node_type, "title": name, "city": city,
                "subtype": subtype, "neighborhood": hood, "latitude": lat, "longitude": lon,
                "maps_query": f"{name}, {city}", "audience_tags": atags, "country_tags": atags,
            }, f"{name} — {subtype} in {hood}. Verify hours and access before visiting.")
            count += 1

    for slug, name, price, dist, ctags, dtags in spec["restaurants"]:
        _write(folder, "restaurants", f"{key}-{slug}", {
            "id": f"restaurant_{key}_{slug}", "type": "Restaurant", "title": name, "city": city,
            "price_level": price, "distance_km": dist, "country_tags": ctags, "diet_tags": dtags,
            "maps_query": f"{name}, {city}",
        }, f"{name} — comfort food connected to your profile context.")
        count += 1

    for slug, name, rtype, needs in spec["resources"]:
        _write(folder, "resources", f"{key}-{slug}", {
            "id": f"resource_{key}_{slug}", "type": "Resource", "title": name, "city": city,
            "resource_type": rtype, "needs": needs,
        }, f"{name} — support for {', '.join(needs)}.")
        count += 1

    for slug, name, start, loc, cat, ctags in spec["events"]:
        _write(folder, "events", f"{key}-{slug}", {
            "id": f"event_{key}_{slug}", "type": "Event", "title": name, "city": city,
            "start_time": start, "location": loc, "category": cat, "country_tags": ctags,
            "maps_query": f"{loc}, {city}", "notes": "Seeded demo event — verify date and venue with organizers.",
        }, f"{name} at {loc}.")
        count += 1

    for slug, name, platform, ctags, utags in spec["groups"]:
        fm = {"id": f"group_{key}_{slug}", "type": "CommunityGroup", "title": name, "city": city,
              "platform": platform, "join_url": f"https://example.test/{key}-{slug}"}
        if ctags:
            fm["country_tags"] = ctags
        if utags:
            fm["university_tags"] = utags
        _write(folder, "groups", f"{key}-{slug}", fm, f"{name} on {platform}. Verify moderation before joining.")
        count += 1

    for slug, title, cat, tags, desc in spec["guides"]:
        _write(folder, "guides", f"{key}-{slug}", {
            "id": f"guide_{key}_{slug}", "type": "Guide", "title": title, "city": city,
            "category": cat, "tags": tags, "description": desc,
        }, desc)
        count += 1

    for slug, title, cat, when, prio, window, deps in spec["tasks"]:
        fm = {"id": f"task_{slug}", "type": "Task", "title": title, "city": city,
              "category": cat, "when": when, "priority": prio, "estimated_day_window": window}
        if deps:
            fm["depends_on"] = deps
        _write(folder, "tasks", f"{key}-{slug}", fm, title)
        count += 1

    return count


def main() -> None:
    total = 0
    for key, spec in CITIES.items():
        n = gen_city(key, spec)
        total += n
        print(f"{spec['name']}: wrote {n} nodes")
    print(f"Total: {total} nodes")


if __name__ == "__main__":
    main()
