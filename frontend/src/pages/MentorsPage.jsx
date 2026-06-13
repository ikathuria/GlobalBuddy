import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client.js";
import { useAuth } from "../contexts/AuthContext.jsx";

function Stars({ value }) {
  const full = Math.round(value);
  return (
    <span className="gb-stars" aria-label={`${value.toFixed(1)} out of 5`}>
      {"★★★★★".slice(0, full)}
      <span className="gb-stars__empty">{"★★★★★".slice(full)}</span>
    </span>
  );
}

function RateRow({ mentor, onRated }) {
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  const rate = async (value) => {
    setBusy(true);
    try {
      const res = await client.post(`/v1/mentors/${encodeURIComponent(mentor.id)}/rate`, { rating: value });
      setDone(true);
      onRated?.(mentor.id, res.data.rating);
    } catch {
      // ignore — keep the row interactive
    } finally {
      setBusy(false);
    }
  };

  if (done) return <span className="gb-mentor-rate__done">Thanks for rating!</span>;

  return (
    <div className="gb-mentor-rate" role="group" aria-label="Rate this mentor">
      <span>Rate:</span>
      {[1, 2, 3, 4, 5].map((n) => (
        <button key={n} type="button" className="gb-mentor-rate__star" disabled={busy} onClick={() => rate(n)}>
          ☆{n}
        </button>
      ))}
    </div>
  );
}

export default function MentorsPage() {
  const { user, accessToken } = useAuth();
  const canRate = Boolean(user && accessToken);
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ city: "", university: "", country: "", expertise: "" });

  const load = (params) => {
    setLoading(true);
    setError(null);
    client
      .get("/v1/mentors", { params })
      .then((r) => setMentors(r.data.items || []))
      .catch((e) => setError(e.response?.data?.detail || "Could not load mentors."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load({});
  }, []);

  const onApply = (e) => {
    e.preventDefault();
    load(filters);
  };

  const onRated = (id, rating) => {
    setMentors((prev) => prev.map((m) => (m.id === id ? { ...m, rating } : m)));
  };

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
        <div className="gb-nav-right">
          <Link to="/become-mentor" className="gb-btn gb-btn-ghost">Become a mentor</Link>
          <Link to="/dashboard" className="gb-btn gb-btn-ghost">Dashboard</Link>
        </div>
      </nav>

      <div className="gb-main">
        <header className="gb-card gb-dash-hero">
          <p className="gb-hero-kicker">Find your guide</p>
          <h1>Mentors</h1>
          <p style={{ color: "var(--gb-muted)", margin: 0 }}>
            Settled students who volunteered to help newcomers. Filter by city, university, country, or expertise.
          </p>
        </header>

        <form className="gb-card gb-mentor-filters" onSubmit={onApply}>
          {["city", "university", "country", "expertise"].map((key) => (
            <input
              key={key}
              value={filters[key]}
              onChange={(e) => setFilters((f) => ({ ...f, [key]: e.target.value }))}
              placeholder={key[0].toUpperCase() + key.slice(1)}
              aria-label={`Filter by ${key}`}
            />
          ))}
          <button type="submit" className="gb-btn gb-btn-primary">Apply</button>
        </form>

        {error && <div className="gb-error">{error}</div>}

        {loading ? (
          <div className="gb-card" style={{ padding: "2rem", textAlign: "center", color: "var(--gb-muted)" }}>
            Loading mentors…
          </div>
        ) : mentors.length === 0 ? (
          <div className="gb-card" style={{ padding: "2rem", textAlign: "center", color: "var(--gb-muted)" }}>
            No mentors match those filters yet.
          </div>
        ) : (
          <div className="gb-feed-grid">
            {mentors.map((m) => (
              <article key={`${m.source}-${m.id}`} className="gb-card gb-mentor-card">
                <div className="gb-mentor-card__head">
                  <strong>{m.name}</strong>
                  {m.rating > 0 && <Stars value={m.rating} />}
                </div>
                <p className="gb-mentor-card__meta">
                  {[m.university, m.city, m.country].filter(Boolean).join(" · ")}
                </p>
                {m.bio && <p className="gb-mentor-card__bio">{m.bio}</p>}
                {m.expertise?.length > 0 && (
                  <div className="gb-chip-row">
                    {m.expertise.slice(0, 5).map((e) => (
                      <span key={e} className="gb-chip gb-chip--soft">{e}</span>
                    ))}
                  </div>
                )}
                {m.source === "seed" && <span className="gb-badge gb-badge--muted">Seed mentor</span>}
                {canRate && m.can_rate && <RateRow mentor={m} onRated={onRated} />}
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
