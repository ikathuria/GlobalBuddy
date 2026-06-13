import { useEffect, useMemo, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import client from "../api/client.js";
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
  { label: "AI Chat", desc: "Ask anything about US life", href: "/chat", icon: "💬", ready: true },
  { label: "My Connections", desc: "Track your intro and connection requests", href: "/connections", icon: "🤝", ready: true },
  { label: "Find Mentors", desc: "Connect with settled students", href: "/mentors", icon: "👥", ready: true },
  { label: "Discover Feed", desc: "Events and guides in your city", href: "/feed", icon: "🌆", ready: true },
];


const STAGE_LABELS = {
  newcomer: "Newcomer",
  settler: "Settler",
  local: "Local",
  mentor: "Mentor",
};

function parseDate(value) {
  if (!value) return null;
  const date = new Date(`${String(value).slice(0, 10)}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

function daysSince(value) {
  const date = parseDate(value);
  if (!date) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const elapsed = today.getTime() - date.getTime();
  return Math.max(0, Math.floor(elapsed / 86_400_000));
}

function monthsRemaining(days) {
  const months = Math.max(1, Math.ceil(days / 30));
  return `${months} ${months === 1 ? "month" : "months"}`;
}

function stageProgress(stage, arrivalDate) {
  const elapsedDays = daysSince(arrivalDate);
  const label = STAGE_LABELS[stage] || STAGE_LABELS.newcomer;

  if (stage === "mentor") {
    return { text: "You're a Mentor - keep guiding the next arrival wave.", percent: 100, canUpgrade: false };
  }

  if (stage === "local") {
    return { text: "You're a Local - mentor opt-in opens when that flow is ready.", percent: 100, canUpgrade: false };
  }

  if (elapsedDays === null) {
    return { text: `You're a ${label} - add an arrival date during profile setup for exact progress.`, percent: 25, canUpgrade: false };
  }

  if (stage === "settler") {
    const daysToLocal = Math.max(0, 365 - elapsedDays);
    return {
      text: daysToLocal > 0 ? `You're a Settler - ${monthsRemaining(daysToLocal)} to Local` : "You're a Settler - ready to mark yourself Local.",
      percent: Math.min(100, Math.round((elapsedDays / 365) * 100)),
      canUpgrade: daysToLocal <= 0,
    };
  }

  const daysToSettler = Math.max(0, 90 - elapsedDays);
  return {
    text: daysToSettler > 0 ? `You're a Newcomer - ${monthsRemaining(daysToSettler)} to Settler` : "You're a Newcomer - ready to mark yourself Settler.",
    percent: Math.min(100, Math.round((elapsedDays / 90) * 100)),
    canUpgrade: daysToSettler <= 0,
  };
}

export default function DashboardPage() {
  const { user, accessToken, signOut } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [profileError, setProfileError] = useState("");
  const [stageSaving, setStageSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      if (!accessToken) {
        setProfile(null);
        setProfileError("");
        return;
      }
      try {
        const response = await client.get("/v1/auth/me");
        if (!cancelled) {
          setProfile(response.data?.profile || null);
          setProfileError("");
        }
      } catch (error) {
        if (!cancelled) setProfileError(error.response?.data?.detail || error.message);
      }
    }

    loadProfile();
    return () => {
      cancelled = true;
    };
  }, [accessToken]);

  const handleSignOut = async () => {
    await signOut();
    navigate("/");
  };

  const handleStageUpgrade = async () => {
    const targetStage = stage === "settler" ? "local" : "settler";
    setStageSaving(true);
    setProfileError("");
    try {
      const response = await client.patch("/v1/auth/me/stage", { stage: targetStage });
      setProfile(response.data?.profile || null);
    } catch (error) {
      setProfileError(error.response?.data?.detail || error.message);
    } finally {
      setStageSaving(false);
    }
  };

  const displayProfile = profile || user || {};
  const stage = displayProfile.stage || "newcomer";
  const stageIndex = Math.max(0, STAGES.findIndex((s) => s.id === stage));
  const progress = useMemo(
    () => stageProgress(stage, displayProfile.arrival_date),
    [stage, displayProfile.arrival_date],
  );
  const upgradeLabel = stage === "settler" ? "Mark me Local" : "Mark me Settler";

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
        <div className="gb-nav-right">
          <span className="gb-nav-user">{displayProfile.email || user?.email}</span>
          <button type="button" className="gb-btn gb-btn-ghost" onClick={handleSignOut}>
            Sign out
          </button>
        </div>
      </nav>

      <div className="gb-main">
        {/* Welcome header */}
        <header className="gb-card gb-dash-hero">
          <p className="gb-hero-kicker">Your community dashboard</p>
          <h1>Welcome{displayProfile.full_name ? `, ${displayProfile.full_name}` : " back"}.</h1>
          <p style={{ color: "var(--gb-muted)", margin: 0 }}>
            You are on your Globalदोस्त journey. Here is your progress and what is waiting for you.
          </p>
        </header>

        {/* Journey stage bar */}
        <section className="gb-card gb-dash-stage" aria-label="Journey stage">
          <h2 className="gb-section-title">Your Journey</h2>
          <div className="gb-stage-summary">
            <strong>{progress.text}</strong>
            <div className="gb-stage-progressbar" aria-label="Journey stage progress">
              <span style={{ width: `${progress.percent}%` }} />
            </div>
          </div>
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
          {accessToken && progress.canUpgrade && stage !== "local" && stage !== "mentor" && (
            <div className="gb-stage-upgrade">
              <div>
                <strong>Your timeline says you may be ready for the next stage.</strong>
                <p>Advance your dashboard so matches emphasize the right people, events, and community support.</p>
              </div>
              <button type="button" className="gb-btn gb-btn-primary gb-btn-sm" onClick={handleStageUpgrade} disabled={stageSaving}>
                {stageSaving ? "Updating..." : upgradeLabel}
              </button>
            </div>
          )}
          {profileError && <p className="gb-stage-error">{profileError}</p>}
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
