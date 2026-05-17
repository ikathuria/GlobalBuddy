// Pre-arrival checklist nodes — things to do BEFORE landing in the US
// Labels: PreArrivalChecklist {id, name, description, when, priority, category}
// when: "before_landing" | "arrival_day" | "first_week"
// priority: "critical" | "high" | "medium" | "low"

CREATE CONSTRAINT pre_arrival_id IF NOT EXISTS FOR (n:PreArrivalChecklist) REQUIRE n.id IS UNIQUE;

// ── Before landing ────────────────────────────────────────────────────────────

MERGE (pa1:PreArrivalChecklist {id: 'pa_print_docs'})
SET pa1.name = 'Print and organise your documents',
    pa1.description = 'Print multiple copies of your I-20, passport photo page, US visa, admission letter, financial documents, and any vaccination records. Keep originals and copies in separate bags.',
    pa1.when = 'before_landing',
    pa1.priority = 'critical',
    pa1.category = 'documents';

MERGE (pa2:PreArrivalChecklist {id: 'pa_iss_email'})
SET pa2.name = 'Email your university International Student Services (ISS)',
    pa2.description = 'Introduce yourself, confirm your arrival date, and ask about the mandatory check-in process. Most universities require you to report within 30 days of the program start date.',
    pa2.when = 'before_landing',
    pa2.priority = 'critical',
    pa2.category = 'university';

MERGE (pa3:PreArrivalChecklist {id: 'pa_temp_housing'})
SET pa3.name = 'Book temporary housing for your first week',
    pa3.description = 'Even if you have a lease starting later, book short-term housing near campus (dorm, Airbnb, extended-stay hotel). Do not arrive without accommodation confirmed.',
    pa3.when = 'before_landing',
    pa3.priority = 'critical',
    pa3.category = 'housing';

MERGE (pa4:PreArrivalChecklist {id: 'pa_travel_insurance'})
SET pa4.name = 'Get travel and health insurance for the gap period',
    pa4.description = 'University health insurance usually starts with the semester. Get a short-term travel health policy (World Nomads, SafetyWing) to cover the period before it activates.',
    pa4.when = 'before_landing',
    pa4.priority = 'high',
    pa4.category = 'health';

MERGE (pa5:PreArrivalChecklist {id: 'pa_notify_bank'})
SET pa5.name = 'Notify your home bank of international travel',
    pa5.description = 'Call or use your bank\'s app to flag that you will be using your card internationally. This prevents fraud blocks when you need cash on arrival.',
    pa5.when = 'before_landing',
    pa5.priority = 'high',
    pa5.category = 'banking';

MERGE (pa6:PreArrivalChecklist {id: 'pa_usd_cash'})
SET pa6.name = 'Exchange at least $200 USD cash before departure',
    pa6.description = 'You will need cash immediately for transport, food, and tips before you have a US bank account or card. Airport exchange rates are bad — use a bank or Wise before you leave.',
    pa6.when = 'before_landing',
    pa6.priority = 'high',
    pa6.category = 'banking';

MERGE (pa7:PreArrivalChecklist {id: 'pa_esim'})
SET pa7.name = 'Get a US eSIM or international SIM before you land',
    pa7.description = 'Airalo, T-Mobile, or Google Fi eSIMs can be set up before departure. You will need data the moment you land for maps, Uber, and contact.',
    pa7.when = 'before_landing',
    pa7.priority = 'high',
    pa7.category = 'connectivity';

MERGE (pa8:PreArrivalChecklist {id: 'pa_offline_maps'})
SET pa8.name = 'Download offline maps for your city',
    pa8.description = 'Open Google Maps and download your target city and campus area for offline use. Also download Maps.me as a backup. You may have unreliable data coverage at first.',
    pa8.when = 'before_landing',
    pa8.priority = 'medium',
    pa8.category = 'connectivity';

MERGE (pa9:PreArrivalChecklist {id: 'pa_medication'})
SET pa9.name = 'Pack 3 months of any prescription medication',
    pa9.description = 'US pharmacies cannot fill foreign prescriptions immediately. Bring enough supply for your first 90 days and carry a copy of the prescription and doctor\'s note in English.',
    pa9.when = 'before_landing',
    pa9.priority = 'medium',
    pa9.category = 'health';

MERGE (pa10:PreArrivalChecklist {id: 'pa_cloud_backup'})
SET pa10.name = 'Back up all documents to cloud storage',
    pa10.description = 'Upload scanned copies of I-20, passport, visa, bank statements, and admission letter to Google Drive or iCloud. You will thank yourself if your bag is lost.',
    pa10.when = 'before_landing',
    pa10.priority = 'medium',
    pa10.category = 'documents';

MERGE (pa11:PreArrivalChecklist {id: 'pa_airport_pickup'})
SET pa11.name = 'Arrange airport pickup or research your route',
    pa11.description = 'Find out whether your university offers free airport pickup for new international students. If not, research Uber/Lyft costs vs. train options in advance — do not figure this out while jet-lagged.',
    pa11.when = 'before_landing',
    pa11.priority = 'medium',
    pa11.category = 'transport';

// ── Arrival day ───────────────────────────────────────────────────────────────

MERGE (pa12:PreArrivalChecklist {id: 'pa_customs_docs'})
SET pa12.name = 'Have I-20, passport, and visa ready at customs',
    pa12.description = 'US Customs and Border Protection will ask for your I-20, passport, and F-1 visa. Keep them in your carry-on, not checked luggage. State you are a student on an F-1 visa.',
    pa12.when = 'arrival_day',
    pa12.priority = 'critical',
    pa12.category = 'documents';

MERGE (pa13:PreArrivalChecklist {id: 'pa_us_sim'})
SET pa13.name = 'Get a US SIM or activate eSIM on arrival',
    pa13.description = 'If you did not get an eSIM before departure, pick up a prepaid SIM at the airport (T-Mobile or AT&T kiosks). Mint Mobile or T-Mobile prepaid gives you the best value.',
    pa13.when = 'arrival_day',
    pa13.priority = 'high',
    pa13.category = 'connectivity';

MERGE (pa14:PreArrivalChecklist {id: 'pa_reach_housing'})
SET pa14.name = 'Get to your housing and confirm check-in',
    pa14.description = 'Confirm your address with your host/dorm before landing. If your check-in time is later than arrival, ask about luggage storage options.',
    pa14.when = 'arrival_day',
    pa14.priority = 'high',
    pa14.category = 'housing';

// ── First week ────────────────────────────────────────────────────────────────

MERGE (pa15:PreArrivalChecklist {id: 'pa_iss_checkin'})
SET pa15.name = 'Check in with ISS and validate your SEVIS record',
    pa15.description = 'This is legally required on an F-1 visa. Bring your I-20, passport, and visa. ISS will validate your SEVIS record and brief you on OPT/CPT, employment rules, and campus resources.',
    pa15.when = 'first_week',
    pa15.priority = 'critical',
    pa15.category = 'university';

MERGE (pa16:PreArrivalChecklist {id: 'pa_bank_account'})
SET pa16.name = 'Open a US bank account',
    pa16.description = 'Chase and Bank of America are the most student-friendly. Bring your passport, I-20, and university admission letter. Some branches also need a local address — use your dorm/apartment.',
    pa16.when = 'first_week',
    pa16.priority = 'critical',
    pa16.category = 'banking';

MERGE (pa17:PreArrivalChecklist {id: 'pa_student_id'})
SET pa17.name = 'Get your university student ID',
    pa17.description = 'Your student ID gives you library access, campus transport discounts, and software licenses. Visit the registrar or ID office — location varies by university.',
    pa17.when = 'first_week',
    pa17.priority = 'high',
    pa17.category = 'university';

MERGE (pa18:PreArrivalChecklist {id: 'pa_health_insurance'})
SET pa18.name = 'Enroll in or waive university health insurance',
    pa18.description = 'Most universities auto-enroll you in their plan and charge it to your account. If you have equivalent coverage, you can waive it — but the window is usually just the first 2 weeks of semester.',
    pa18.when = 'first_week',
    pa18.priority = 'high',
    pa18.category = 'health';

MERGE (pa19:PreArrivalChecklist {id: 'pa_grocery_run'})
SET pa19.name = 'Do a grocery run and learn your neighborhood',
    pa19.description = 'Walk or take transit to find your nearest grocery store, pharmacy, laundromat, and any culturally relevant food store. Knowing these early saves stress.',
    pa19.when = 'first_week',
    pa19.priority = 'medium',
    pa19.category = 'local';

// ── Document Task nodes (linked to plan topological order) ────────────────────
// These Task nodes appear in plan generation; PRECEDES edges ensure correct sequence.

CREATE CONSTRAINT task_id IF NOT EXISTS FOR (n:Task) REQUIRE n.id IS UNIQUE;

MERGE (t_identity:Task {id: 'task_identity_docs'})
SET t_identity.name = 'Organise identity documents',
    t_identity.estimated_day_window = 'Day 1-2',
    t_identity.category = 'documents';

MERGE (t_iss:Task {id: 'task_iss_checkin'})
SET t_iss.name = 'Check in with International Student Services (ISS)',
    t_iss.estimated_day_window = 'Day 1-3',
    t_iss.category = 'university';

MERGE (t_bank:Task {id: 'task_open_bank'})
SET t_bank.name = 'Open a US bank account',
    t_bank.estimated_day_window = 'Day 3-7',
    t_bank.category = 'banking';

MERGE (t_health:Task {id: 'task_health_insurance'})
SET t_health.name = 'Confirm or enroll in health insurance',
    t_health.estimated_day_window = 'Day 1-14',
    t_health.category = 'health';

MERGE (t_ssn:Task {id: 'task_ssn'})
SET t_ssn.name = 'Apply for Social Security Number (SSN) if eligible',
    t_ssn.estimated_day_window = 'Day 14-30',
    t_ssn.category = 'documents';

MERGE (t_housing:Task {id: 'task_housing'})
SET t_housing.name = 'Confirm long-term housing or lease',
    t_housing.estimated_day_window = 'Day 1-14',
    t_housing.category = 'housing';

// Topological order: identity → ISS → bank → SSN; health and housing run in parallel
MERGE (t_identity)-[:PRECEDES]->(t_iss);
MERGE (t_iss)-[:PRECEDES]->(t_bank);
MERGE (t_bank)-[:PRECEDES]->(t_ssn);
