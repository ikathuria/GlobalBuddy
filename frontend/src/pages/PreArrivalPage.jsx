import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client.js";

const WHEN_LABELS = {
  before_landing: "Before You Land",
  arrival_day: "Arrival Day",
  first_week: "First Week",
};

const WHEN_ORDER = ["before_landing", "arrival_day", "first_week"];

const PRIORITY_COLORS = {
  critical: "gb-priority--critical",
  high: "gb-priority--high",
  medium: "gb-priority--medium",
  low: "gb-priority--low",
};

const STORAGE_KEY = "gb_pre_arrival_done";

function loadDone() {
  try { return new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]")); }
  catch { return new Set(); }
}

function saveDone(set) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
}

export default function PreArrivalPage() {
  const [items, setItems] = useState([]);
  const [done, setDone] = useState(loadDone);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeWhen, setActiveWhen] = useState("before_landing");
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    client.get("/v1/pre-arrival/checklist")
      .then(r => setItems(r.data))
      .catch(() => {
        // API not seeded yet — use built-in fallback data
        setItems(FALLBACK_ITEMS);
      })
      .finally(() => setLoading(false));
  }, []);

  const toggle = (id) => {
    setDone(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      saveDone(next);
      return next;
    });
  };

  const byWhen = WHEN_ORDER.reduce((acc, w) => {
    acc[w] = items.filter(i => i.when === w);
    return acc;
  }, {});

  const total = items.length;
  const doneCount = items.filter(i => done.has(i.id)).length;
  const pct = total ? Math.round((doneCount / total) * 100) : 0;

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
        <div className="gb-nav-right">
          <Link to="/" className="gb-btn gb-btn-ghost">Back to Onboarding</Link>
        </div>
      </nav>

      <div className="gb-main">
        <header className="gb-card gb-pa-hero">
          <p className="gb-hero-kicker">Before you arrive</p>
          <h1>Pre-Arrival Checklist</h1>
          <p style={{ color: "var(--gb-muted)", margin: 0 }}>
            {total} things to prepare before and after you land — so your first days feel calm, not chaotic.
          </p>

          {/* Progress bar */}
          <div className="gb-pa-progress" aria-label={`${doneCount} of ${total} complete`}>
            <div className="gb-pa-progress-bar" style={{ width: `${pct}%` }} />
          </div>
          <p className="gb-pa-progress-label">
            {doneCount} / {total} done {pct === 100 ? "🎉 You are ready!" : ""}
          </p>
        </header>

        {/* Phase tabs */}
        <div className="gb-pa-tabs" role="tablist">
          {WHEN_ORDER.map(w => (
            <button
              key={w}
              role="tab"
              aria-selected={activeWhen === w}
              className={`gb-pa-tab ${activeWhen === w ? "gb-pa-tab--active" : ""}`}
              onClick={() => setActiveWhen(w)}
            >
              {WHEN_LABELS[w]}
              <span className="gb-pa-tab-count">
                {byWhen[w].filter(i => done.has(i.id)).length}/{byWhen[w].length}
              </span>
            </button>
          ))}
        </div>

        {loading ? (
          <div className="gb-card" style={{ padding: "2rem", textAlign: "center", color: "var(--gb-muted)" }}>
            Loading checklist…
          </div>
        ) : (
          <ul className="gb-pa-list">
            {byWhen[activeWhen].map(item => (
              <li key={item.id} className={`gb-pa-item gb-card ${done.has(item.id) ? "gb-pa-item--done" : ""}`}>
                <div className="gb-pa-item-row">
                  <button
                    type="button"
                    className="gb-pa-checkbox"
                    aria-label={done.has(item.id) ? "Mark incomplete" : "Mark complete"}
                    aria-pressed={done.has(item.id)}
                    onClick={() => toggle(item.id)}
                  >
                    {done.has(item.id) ? "✓" : ""}
                  </button>

                  <div className="gb-pa-item-body">
                    <div className="gb-pa-item-head">
                      <span className={`gb-priority-badge ${PRIORITY_COLORS[item.priority] || ""}`}>
                        {item.priority}
                      </span>
                      <span className="gb-pa-item-name">{item.name}</span>
                    </div>

                    {expanded === item.id && (
                      <p className="gb-pa-item-desc">{item.description}</p>
                    )}
                  </div>

                  <button
                    type="button"
                    className="gb-pa-expand"
                    aria-label={expanded === item.id ? "Collapse" : "Expand"}
                    onClick={() => setExpanded(expanded === item.id ? null : item.id)}
                  >
                    {expanded === item.id ? "▲" : "▼"}
                  </button>
                </div>
              </li>
            ))}

            {byWhen[activeWhen].length === 0 && (
              <li className="gb-card" style={{ padding: "1.5rem", color: "var(--gb-muted)", textAlign: "center" }}>
                No items for this phase.
              </li>
            )}
          </ul>
        )}

        <div className="gb-pa-footer-note">
          <p>Progress is saved in your browser. Create an account to sync across devices.</p>
          <Link to="/auth" className="gb-btn gb-btn-primary">Create account</Link>
        </div>
      </div>
    </div>
  );
}

// ── Fallback data when API/Neo4j is not seeded ────────────────────────────────

const FALLBACK_ITEMS = [
  { id: "pa_print_docs", name: "Print and organise your documents", description: "Print multiple copies of your I-20, passport, US visa, admission letter, and financial documents. Keep originals and copies in separate bags.", when: "before_landing", priority: "critical", category: "documents" },
  { id: "pa_iss_email", name: "Email your university International Student Services (ISS)", description: "Introduce yourself, confirm your arrival date, and ask about the mandatory check-in process.", when: "before_landing", priority: "critical", category: "university" },
  { id: "pa_temp_housing", name: "Book temporary housing for your first week", description: "Even if you have a lease starting later, book short-term housing near campus.", when: "before_landing", priority: "critical", category: "housing" },
  { id: "pa_travel_insurance", name: "Get travel and health insurance for the gap period", description: "University health insurance usually starts with the semester. Get a short-term travel health policy to cover the gap.", when: "before_landing", priority: "high", category: "health" },
  { id: "pa_notify_bank", name: "Notify your home bank of international travel", description: "Call or use your bank's app to flag international use. This prevents fraud blocks when you need cash on arrival.", when: "before_landing", priority: "high", category: "banking" },
  { id: "pa_usd_cash", name: "Exchange at least $200 USD cash before departure", description: "You will need cash before you have a US bank account. Use a bank or Wise before you leave — airport rates are poor.", when: "before_landing", priority: "high", category: "banking" },
  { id: "pa_esim", name: "Get a US eSIM or international SIM before you land", description: "Airalo, T-Mobile, or Google Fi eSIMs can be set up before departure. You will need data the moment you land.", when: "before_landing", priority: "high", category: "connectivity" },
  { id: "pa_offline_maps", name: "Download offline maps for your city", description: "Open Google Maps and download your target city and campus area for offline use.", when: "before_landing", priority: "medium", category: "connectivity" },
  { id: "pa_medication", name: "Pack 3 months of any prescription medication", description: "US pharmacies cannot fill foreign prescriptions immediately. Bring enough supply and a copy of the prescription in English.", when: "before_landing", priority: "medium", category: "health" },
  { id: "pa_cloud_backup", name: "Back up all documents to cloud storage", description: "Upload scanned copies of I-20, passport, visa, and bank statements to Google Drive or iCloud.", when: "before_landing", priority: "medium", category: "documents" },
  { id: "pa_airport_pickup", name: "Arrange airport pickup or research your route", description: "Check if your university offers free airport pickup. If not, research Uber/Lyft vs. train options in advance.", when: "before_landing", priority: "medium", category: "transport" },
  { id: "pa_customs_docs", name: "Have I-20, passport, and visa ready at customs", description: "US Customs will ask for your I-20, passport, and F-1 visa. Keep them in your carry-on. State you are a student on an F-1 visa.", when: "arrival_day", priority: "critical", category: "documents" },
  { id: "pa_us_sim", name: "Get a US SIM or activate eSIM on arrival", description: "Pick up a prepaid SIM at the airport (T-Mobile or AT&T kiosks) if you did not arrange one beforehand.", when: "arrival_day", priority: "high", category: "connectivity" },
  { id: "pa_reach_housing", name: "Get to your housing and confirm check-in", description: "Confirm your address before landing. If check-in is later than arrival, ask about luggage storage.", when: "arrival_day", priority: "high", category: "housing" },
  { id: "pa_iss_checkin", name: "Check in with ISS and validate your SEVIS record", description: "Legally required on an F-1 visa. Bring your I-20, passport, and visa. ISS will validate your SEVIS record.", when: "first_week", priority: "critical", category: "university" },
  { id: "pa_bank_account", name: "Open a US bank account", description: "Chase and Bank of America are the most student-friendly. Bring passport, I-20, and university admission letter.", when: "first_week", priority: "critical", category: "banking" },
  { id: "pa_student_id", name: "Get your university student ID", description: "Your student ID gives you library access, campus transport discounts, and software licences.", when: "first_week", priority: "high", category: "university" },
  { id: "pa_health_insurance", name: "Enroll in or waive university health insurance", description: "Most universities auto-enroll you. If you have equivalent coverage, you can waive it — the window is usually just the first 2 weeks.", when: "first_week", priority: "high", category: "health" },
  { id: "pa_grocery_run", name: "Do a grocery run and learn your neighbourhood", description: "Walk or take transit to find your nearest grocery store, pharmacy, and laundromat. Knowing these early saves stress.", when: "first_week", priority: "medium", category: "local" },
];
