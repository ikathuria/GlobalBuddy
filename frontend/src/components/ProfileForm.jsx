import { useState } from "react";
import client from "../api/client.js";

const defaultProfile = {
  country_of_origin: "India",
  home_city: "Bengaluru",
  target_university: "Illinois Institute of Technology",
  target_city: "Chicago",
  needs: "banking, housing, community",
  interests: "south indian food, hackathons, tech meetups, Luma events",
  cultural_background: "South Indian",
  religion_or_observance: "Hindu",
  diet: "vegetarian",
};

export default function ProfileForm({ onMatch }) {
  const [form, setForm] = useState(defaultProfile);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        country_of_origin: form.country_of_origin.trim(),
        home_city: form.home_city.trim(),
        target_university: form.target_university.trim(),
        target_city: form.target_city.trim(),
        needs: form.needs.split(",").map((s) => s.trim()).filter(Boolean),
        interests: form.interests.split(",").map((s) => s.trim()).filter(Boolean),
      };
      const res = await client.post("/v1/profile/match", payload);
      onMatch(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="gb-card">
      <h2>Your profile</h2>
      <p style={{ margin: "0 0 1rem", color: "var(--gb-muted)", fontSize: "0.9rem" }}>
        We query Neo4j for mentors, peers, restaurants, events, resources, and Chicago local nodes (worship, groceries,
        housing, exploration, transit) — then build a subgraph for the canvas.
      </p>
      <form onSubmit={submit}>
        <div className="gb-form-grid">
          <label className="gb-field">
            <span>Country of origin</span>
            <input
              value={form.country_of_origin}
              onChange={(e) => setForm({ ...form, country_of_origin: e.target.value })}
              autoComplete="country-name"
            />
          </label>
          <label className="gb-field">
            <span>Home city</span>
            <input
              value={form.home_city}
              onChange={(e) => setForm({ ...form, home_city: e.target.value })}
            />
          </label>
          <label className="gb-field">
            <span>Target university</span>
            <input
              value={form.target_university}
              onChange={(e) => setForm({ ...form, target_university: e.target.value })}
            />
          </label>
          <label className="gb-field">
            <span>Target city</span>
            <input
              value={form.target_city}
              onChange={(e) => setForm({ ...form, target_city: e.target.value })}
            />
          </label>
          <label className="gb-field gb-field--full">
            <span>Needs (comma-separated)</span>
            <input
              value={form.needs}
              onChange={(e) => setForm({ ...form, needs: e.target.value })}
              placeholder="banking, housing, orientation…"
            />
          </label>
          <label className="gb-field gb-field--full">
            <span>Interests (comma-separated)</span>
            <input
              value={form.interests}
              onChange={(e) => setForm({ ...form, interests: e.target.value })}
            />
          </label>
          <label className="gb-field gb-field--full">
            <span>Cultural background (optional)</span>
            <input
              value={form.cultural_background}
              onChange={(e) => setForm({ ...form, cultural_background: e.target.value })}
              placeholder="e.g. South Asian"
            />
          </label>
          <label className="gb-field">
            <span>Religion / observance (optional)</span>
            <input
              value={form.religion_or_observance}
              onChange={(e) => setForm({ ...form, religion_or_observance: e.target.value })}
              placeholder="Hindu, Muslim, Sikh…"
            />
          </label>
          <label className="gb-field">
            <span>Diet (optional)</span>
            <input value={form.diet} onChange={(e) => setForm({ ...form, diet: e.target.value })} placeholder="vegetarian, halal…" />
          </label>
        </div>
        <div style={{ marginTop: "1.15rem" }}>
          <button type="submit" className="gb-btn gb-btn-primary" disabled={loading}>
            {loading ? "Querying graph…" : "Run graph match"}
          </button>
        </div>
      </form>
      {error && <div className="gb-error">{typeof error === "string" ? error : JSON.stringify(error)}</div>}
    </section>
  );
}
