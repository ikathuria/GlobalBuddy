import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import client from "../api/client.js";
import { useAuth } from "../contexts/AuthContext.jsx";

const ELIGIBLE = new Set(["settler", "local", "mentor"]);

export default function BecomeMentorPage() {
  const { user, accessToken, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [state, setState] = useState({ loading: true, profile: null, error: null });
  const [form, setForm] = useState({ expertise: "", availability: "available", bio: "" });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    if (!user || !accessToken) {
      navigate("/auth");
      return;
    }
    client
      .get("/v1/mentors/me")
      .then((r) => {
        setState({ loading: false, profile: r.data, error: null });
        if (r.data.opted_in) {
          setForm({
            expertise: (r.data.expertise || []).join(", "),
            availability: r.data.availability || "available",
            bio: r.data.bio || "",
          });
        }
      })
      .catch((e) => setState({ loading: false, profile: null, error: e.response?.data?.detail || "Could not load your profile." }));
  }, [authLoading, user, accessToken, navigate]);

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await client.post("/v1/mentors/opt-in", {
        expertise: form.expertise.split(",").map((s) => s.trim()).filter(Boolean),
        availability: form.availability,
        bio: form.bio,
      });
      setSaved(true);
    } catch (err) {
      setState((s) => ({ ...s, error: err.response?.data?.detail || "Could not save. Please try again." }));
    } finally {
      setSaving(false);
    }
  };

  const stage = state.profile?.stage || "newcomer";
  const eligible = ELIGIBLE.has(stage);

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
        <div className="gb-nav-right">
          <Link to="/mentors" className="gb-btn gb-btn-ghost">All mentors</Link>
          <Link to="/dashboard" className="gb-btn gb-btn-ghost">Dashboard</Link>
        </div>
      </nav>

      <div className="gb-main">
        <header className="gb-card gb-dash-hero">
          <p className="gb-hero-kicker">Give back</p>
          <h1>Become a mentor</h1>
          <p style={{ color: "var(--gb-muted)", margin: 0 }}>
            Once you've settled in, help the next wave of newcomers. Opting in is always your choice — and you can pause anytime.
          </p>
        </header>

        {state.loading ? (
          <div className="gb-card" style={{ padding: "2rem", textAlign: "center", color: "var(--gb-muted)" }}>Loading…</div>
        ) : saved ? (
          <div className="gb-card" style={{ padding: "2rem" }}>
            <h2 style={{ marginTop: 0 }}>You're a mentor 🎉</h2>
            <p style={{ color: "var(--gb-muted)" }}>Your profile is live in the mentor directory. Thank you for giving back.</p>
            <Link to="/mentors" className="gb-btn gb-btn-primary">View the directory</Link>
          </div>
        ) : !eligible ? (
          <div className="gb-card" style={{ padding: "2rem" }}>
            <h2 style={{ marginTop: 0 }}>Not quite yet</h2>
            <p style={{ color: "var(--gb-muted)" }}>
              Mentoring opens once you reach the <strong>Settler</strong> stage (3+ months settled). You're currently a{" "}
              <strong>{stage}</strong>. Keep going — your dashboard shows your progress.
            </p>
            <Link to="/dashboard" className="gb-btn gb-btn-secondary">Back to dashboard</Link>
          </div>
        ) : (
          <form className="gb-card gb-mentor-form" onSubmit={submit}>
            {state.profile?.opted_in && (
              <p className="gb-badge gb-badge--accent" style={{ marginLeft: 0 }}>Editing your existing mentor profile</p>
            )}
            <label>
              <span>Areas you can help with</span>
              <input
                value={form.expertise}
                onChange={(e) => setForm((f) => ({ ...f, expertise: e.target.value }))}
                placeholder="banking, housing, visa, campus life (comma-separated)"
              />
            </label>
            <label>
              <span>Availability</span>
              <select value={form.availability} onChange={(e) => setForm((f) => ({ ...f, availability: e.target.value }))}>
                <option value="available">Available</option>
                <option value="paused">Paused</option>
              </select>
            </label>
            <label>
              <span>Short bio</span>
              <textarea
                rows={4}
                value={form.bio}
                onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))}
                placeholder="What you wish someone had told you in your first month."
              />
            </label>
            {state.error && <div className="gb-error">{state.error}</div>}
            <button type="submit" className="gb-btn gb-btn-primary" disabled={saving}>
              {saving ? "Saving…" : state.profile?.opted_in ? "Update profile" : "Opt in as a mentor"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
