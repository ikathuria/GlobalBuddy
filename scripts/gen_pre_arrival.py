"""One-off generator: pre-arrival checklist Markdown nodes from the legacy Cypher seed content."""

from pathlib import Path

ITEMS = [
    ("pa_print_docs", "Print and organise your documents", "before_landing", "critical", "documents",
     "Print multiple copies of your I-20, passport photo page, US visa, admission letter, financial documents, and any vaccination records. Keep originals and copies in separate bags."),
    ("pa_iss_email", "Email your university International Student Services (ISS)", "before_landing", "critical", "university",
     "Introduce yourself, confirm your arrival date, and ask about the mandatory check-in process. Most universities require you to report within 30 days of the program start date."),
    ("pa_temp_housing", "Book temporary housing for your first week", "before_landing", "critical", "housing",
     "Even if you have a lease starting later, book short-term housing near campus (dorm, Airbnb, extended-stay hotel). Do not arrive without accommodation confirmed."),
    ("pa_travel_insurance", "Get travel and health insurance for the gap period", "before_landing", "high", "health",
     "University health insurance usually starts with the semester. Get a short-term travel health policy (World Nomads, SafetyWing) to cover the period before it activates."),
    ("pa_notify_bank", "Notify your home bank of international travel", "before_landing", "high", "banking",
     "Call or use your bank's app to flag that you will be using your card internationally. This prevents fraud blocks when you need cash on arrival."),
    ("pa_usd_cash", "Exchange at least $200 USD cash before departure", "before_landing", "high", "banking",
     "You will need cash immediately for transport, food, and tips before you have a US bank account or card. Airport exchange rates are bad - use a bank or Wise before you leave."),
    ("pa_esim", "Get a US eSIM or international SIM before you land", "before_landing", "high", "connectivity",
     "Airalo, T-Mobile, or Google Fi eSIMs can be set up before departure. You will need data the moment you land for maps, Uber, and contact."),
    ("pa_offline_maps", "Download offline maps for your city", "before_landing", "medium", "connectivity",
     "Open Google Maps and download your target city and campus area for offline use. Also download Maps.me as a backup. You may have unreliable data coverage at first."),
    ("pa_medication", "Pack 3 months of any prescription medication", "before_landing", "medium", "health",
     "US pharmacies cannot fill foreign prescriptions immediately. Bring enough supply for your first 90 days and carry a copy of the prescription and doctor's note in English."),
    ("pa_cloud_backup", "Back up all documents to cloud storage", "before_landing", "medium", "documents",
     "Upload scanned copies of I-20, passport, visa, bank statements, and admission letter to Google Drive or iCloud. You will thank yourself if your bag is lost."),
    ("pa_airport_pickup", "Arrange airport pickup or research your route", "before_landing", "medium", "transport",
     "Find out whether your university offers free airport pickup for new international students. If not, research Uber/Lyft costs vs. train options in advance - do not figure this out while jet-lagged."),
    ("pa_customs_docs", "Have I-20, passport, and visa ready at customs", "arrival_day", "critical", "documents",
     "US Customs and Border Protection will ask for your I-20, passport, and F-1 visa. Keep them in your carry-on, not checked luggage. State you are a student on an F-1 visa."),
    ("pa_us_sim", "Get a US SIM or activate eSIM on arrival", "arrival_day", "high", "connectivity",
     "If you did not get an eSIM before departure, pick up a prepaid SIM at the airport (T-Mobile or AT&T kiosks). Mint Mobile or T-Mobile prepaid gives you the best value."),
    ("pa_reach_housing", "Get to your housing and confirm check-in", "arrival_day", "high", "housing",
     "Confirm your address with your host/dorm before landing. If your check-in time is later than arrival, ask about luggage storage options."),
    ("pa_iss_checkin", "Check in with ISS and validate your SEVIS record", "first_week", "critical", "university",
     "This is legally required on an F-1 visa. Bring your I-20, passport, and visa. ISS will validate your SEVIS record and brief you on OPT/CPT, employment rules, and campus resources."),
    ("pa_bank_account", "Open a US bank account", "first_week", "critical", "banking",
     "Chase and Bank of America are the most student-friendly. Bring your passport, I-20, and university admission letter. Some branches also need a local address - use your dorm/apartment."),
    ("pa_student_id", "Get your university student ID", "first_week", "high", "university",
     "Your student ID gives you library access, campus transport discounts, and software licenses. Visit the registrar or ID office - location varies by university."),
    ("pa_health_insurance", "Enroll in or waive university health insurance", "first_week", "high", "health",
     "Most universities auto-enroll you in their plan and charge it to your account. If you have equivalent coverage, you can waive it - but the window is usually just the first 2 weeks of semester."),
    ("pa_grocery_run", "Do a grocery run and learn your neighborhood", "first_week", "medium", "local",
     "Walk or take transit to find your nearest grocery store, pharmacy, laundromat, and any culturally relevant food store. Knowing these early saves stress."),
]

TEMPLATE = """---
id: {id}
type: PreArrivalChecklist
title: {title}
when: {when}
priority: {priority}
category: {category}
description: >-
  {description}
---

# {title}

{description}
"""


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data" / "graph" / "common" / "pre-arrival"
    out_dir.mkdir(parents=True, exist_ok=True)
    for item_id, title, when, priority, category, description in ITEMS:
        slug = item_id.removeprefix("pa_").replace("_", "-")
        path = out_dir / f"{slug}.md"
        path.write_text(
            TEMPLATE.format(id=item_id, title=title, when=when, priority=priority, category=category, description=description),
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {path.relative_to(out_dir.parents[2])}")


if __name__ == "__main__":
    main()
