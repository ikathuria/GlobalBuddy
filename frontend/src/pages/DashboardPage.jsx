import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";
import DocumentTracker from "../components/DocumentTracker.jsx";

const STAGES = [
  { id: "newcomer", label: "Newcomer", desc: "First 3 months", icon: "✈️" },
  { id: "settler", label: "Settler", desc: "3–12 months", icon: "🏠" },
  { id: "local", label: "Local", desc: "1–2 years", icon: "🗺️" },
  { id: "mentor", label: "Mentor", desc: "Give back", icon: "🤝" },
];

const QUICK_ACTIONS = [
  { label: "Continue Onboarding", desc: "Pick up your 3-step arrival plan", href: "/", icon: "📋", ready: true },
  { label: "Pre-Arrival Checklist", desc: "Prepare before you land", href: "/pre-arrival", icon: "✈️", ready: true },
  { label: "AI Chat", desc: "Ask anything about US life", href: "/chat", icon: "💬", ready: false },
  { label: "Find Mentors", desc: "Connect with settled students", href: "/mentors", icon: "👥", ready: false },
  { label: "Discover Feed", desc: "Events and guides in your city", href: "/feed", icon: "🌆", ready: false },
];


export default function DashboardPage() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate("/");
  };

  const stage = user?.stage || "newcomer";
  const stageIndex = STAGES.findIndex((s) => s.id === stage);

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
        <div className="gb-nav-right">
          <span className="gb-nav-user">{user?.email}</span>
          <button type="button" className="gb-btn gb-btn-ghost" onClick={handleSignOut}>
            Sign out
          </button>
        </div>
      </nav>

      <div className="gb-main">
        {/* Welcome header */}
        <header className="gb-card gb-dash-hero">
          <p className="gb-hero-kicker">Your community dashboard</p>
          <h1>Welcome{user?.full_name ? `, ${user.full_name}` : " back"}.</h1>
          <p style={{ color: "var(--gb-muted)", margin: 0 }}>
            You are on your Globalदोस्त journey. Here is your progress and what is waiting for you.
          </p>
        </header>

        {/* Journey stage bar */}
        <section className="gb-card gb-dash-stage" aria-label="Journey stage">
          <h2 className="gb-section-title">Your Journey</h2>
          <div className="gb-stage-track">
            {STAGES.map((s, i) => (
              <div
                key={s.id}
                className={`gb-stage-step ${i === stageIndex ? "gb-stage-step--active" : ""} ${i < stageIndex ? "gb-stage-step--done" : ""}`}
              >
                <span className="gb-stage-icon">{s.icon}</span>
                <span className="gb-stage-label">{s.label}</span>
                <span className="gb-stage-desc">{s.desc}</span>
              </div>
            ))}
          </div>
          {stageIndex < STAGES.length - 1 && (
            <p className="gb-stage-hint">
              Next: <strong>{STAGES[stageIndex + 1].label}</strong> — {STAGES[stageIndex + 1].desc}
            </p>
          )}
        </section>

        {/* Quick actions */}
        <section aria-label="Quick actions">
          <h2 className="gb-section-title">What would you like to do?</h2>
          <div className="gb-action-grid">
            {QUICK_ACTIONS.map((a) => (
              <div key={a.label} className={`gb-card gb-action-card ${!a.ready ? "gb-action-card--soon" : ""}`}>
                <span className="gb-action-icon">{a.icon}</span>
                <strong>{a.label}</strong>
                <p>{a.desc}</p>
                {a.ready ? (
                  <Link to={a.href} className="gb-btn gb-btn-primary gb-btn-sm">
                    Open
                  </Link>
                ) : (
                  <span className="gb-badge gb-badge--muted">Coming soon</span>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Document tracker */}
        <section className="gb-card gb-dash-docs" aria-label="Document tracker">
          <DocumentTracker />
        </section>
      </div>
    </div>
  );
}
