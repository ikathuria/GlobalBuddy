import { useState } from "react";

const STORAGE_KEY = "gb_doc_tracker";

const DOCUMENTS = [
  {
    id: "ssn",
    label: "Social Security Number (SSN)",
    description: "F-1 students need an employment authorisation (on-campus job or CPT/OPT) before applying. Visit your local SSA office with I-20, passport, visa, and an employment letter.",
    link: "https://www.ssa.gov/ssnumber/",
    linkLabel: "SSA website",
    when: "Day 14–30 (after employment auth)",
  },
  {
    id: "bank",
    label: "US Bank Account",
    description: "Open at Chase, Bank of America, or a credit union near campus. Bring passport, I-20, and admission letter. Some branches also ask for a local address.",
    when: "Day 3–7",
  },
  {
    id: "health_insurance",
    label: "Health Insurance",
    description: "Most universities auto-enroll you in their plan. Log in to your student portal to confirm enrollment, or waive it if you have equivalent coverage — window is usually first 2 weeks.",
    when: "Day 1–14",
  },
  {
    id: "student_id",
    label: "University Student ID",
    description: "Visit the registrar or ID office on campus. You will need it for library access, campus transit discounts, and software licences.",
    when: "Day 1–3",
  },
  {
    id: "i20_copy",
    label: "I-20 Copy (printed)",
    description: "Keep a printed copy of your I-20 separate from the original. You will need it for banking, SSN application, and any off-campus employment paperwork.",
    when: "Before you land",
  },
  {
    id: "lease",
    label: "Signed Lease / Housing Agreement",
    description: "Confirm your long-term lease and get a signed copy. You will need the address for your SSN application and some banks require it too.",
    when: "Day 1–14",
  },
];

const STATUS_CYCLE = ["pending", "in_progress", "done"];
const STATUS_LABELS = { pending: "Pending", in_progress: "In progress", done: "Done" };
const STATUS_ICONS = { pending: "○", in_progress: "◑", done: "●" };

function loadState() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); }
  catch { return {}; }
}

function saveState(s) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
}

export default function DocumentTracker() {
  const [statuses, setStatuses] = useState(loadState);
  const [expanded, setExpanded] = useState(null);

  const advance = (id) => {
    setStatuses(prev => {
      const current = prev[id] || "pending";
      const next = STATUS_CYCLE[(STATUS_CYCLE.indexOf(current) + 1) % STATUS_CYCLE.length];
      const updated = { ...prev, [id]: next };
      saveState(updated);
      return updated;
    });
  };

  const doneCount = DOCUMENTS.filter(d => (statuses[d.id] || "pending") === "done").length;

  return (
    <div className="gb-doc-tracker">
      <div className="gb-doc-tracker-header">
        <h2 className="gb-section-title" style={{ margin: 0 }}>Document Tracker</h2>
        <span className="gb-doc-tracker-count">{doneCount} / {DOCUMENTS.length} done</span>
      </div>
      <p className="gb-doc-tracker-hint">
        Tap the status icon to cycle: Pending → In progress → Done.
      </p>

      <ul className="gb-doc-list">
        {DOCUMENTS.map(doc => {
          const status = statuses[doc.id] || "pending";
          const isOpen = expanded === doc.id;
          return (
            <li key={doc.id} className={`gb-doc-item gb-doc-item--${status}`}>
              <button
                type="button"
                className={`gb-doc-status-btn gb-doc-status-btn--${status}`}
                aria-label={`Status: ${STATUS_LABELS[status]}. Click to advance.`}
                onClick={() => advance(doc.id)}
                title="Click to advance status"
              >
                {STATUS_ICONS[status]}
              </button>

              <div className="gb-doc-content">
                <div className="gb-doc-main">
                  <span className="gb-doc-label">{doc.label}</span>
                  <span className="gb-doc-when">{doc.when}</span>
                </div>

                {isOpen && (
                  <div className="gb-doc-drawer">
                    <p>{doc.description}</p>
                    {doc.link && (
                      <a href={doc.link} target="_blank" rel="noopener noreferrer" className="gb-doc-link">
                        {doc.linkLabel} ↗
                      </a>
                    )}
                  </div>
                )}
              </div>

              <button
                type="button"
                className="gb-doc-expand-btn"
                aria-label={isOpen ? "Collapse" : "Show details"}
                onClick={() => setExpanded(isOpen ? null : doc.id)}
              >
                {isOpen ? "▲" : "▼"}
              </button>

              <span className={`gb-doc-tag gb-doc-tag--${status}`}>
                {STATUS_LABELS[status]}
              </span>
            </li>
          );
        })}
      </ul>

      <p className="gb-dash-note">
        Status saves in your browser. Supabase sync coming in Milestone 5.
      </p>
    </div>
  );
}
