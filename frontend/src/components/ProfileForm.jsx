import { useState } from "react";
import client from "../api/client.js";

const defaultProfile = {
  full_name: "",
  email: "",
  country_of_origin: "India",
  home_city: "Bengaluru",
  target_university: "Illinois Institute of Technology",
  target_city: "Chicago",
  needs: "banking, housing, community",
  interests: "south indian food, hackathons, tech meetups, Luma events",
  cultural_background: "South Indian",
  religion_or_observance: "Hindu",
  diet: "vegetarian",
  linkedin_url: "",
  instagram_url: "",
  other_social_url: "",
  new_to_us: true,
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
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        country_of_origin: form.country_of_origin.trim(),
        home_city: form.home_city.trim(),
        target_university: form.target_university.trim(),
        target_city: form.target_city.trim(),
        needs: form.needs
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        interests: form.interests
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        new_to_us: Boolean(form.new_to_us),
        cultural_background: form.cultural_background.trim(),
        religion_or_observance: form.religion_or_observance.trim(),
        diet: form.diet.trim(),
        linkedin_url: form.linkedin_url.trim(),
        instagram_url: form.instagram_url.trim(),
        other_social_url: form.other_social_url.trim(),
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
      <h2 className="gb-card-title--plain">Step 1: Profile setup</h2>
      <p style={{ margin: "0 0 1rem", color: "var(--gb-muted)", fontSize: "0.9rem" }}>
        We save these details to Neo4j, run your graph match, and decide whether to start in Survival mode or Explore mode.
      </p>
      <div className="gb-profile-hints" aria-label="Profile setup tips">
        <span className="gb-profile-hint">Takes about 1 minute</span>
        <span className="gb-profile-hint">You can edit this later</span>
        <span className="gb-profile-hint">No sensitive documents needed</span>
      </div>
      <form onSubmit={submit}>
        <div className="gb-form-grid">
          <label className="gb-field">
            <span>Full name</span>
            <input
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              autoComplete="name"
              placeholder="Your full name"
              required
            />
          </label>
          <label className="gb-field">
            <span>Email address</span>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              autoComplete="email"
              placeholder="name@example.com"
              required
            />
          </label>
          <label className="gb-field">
            <span>Country of origin</span>
            <input
              value={form.country_of_origin}
              onChange={(e) => setForm({ ...form, country_of_origin: e.target.value })}
              autoComplete="country-name"
              required
            />
          </label>
          <label className="gb-field">
            <span>Home city</span>
            <input value={form.home_city} onChange={(e) => setForm({ ...form, home_city: e.target.value })} required />
          </label>
          <label className="gb-field">
            <span>Target university</span>
            <input
              value={form.target_university}
              onChange={(e) => setForm({ ...form, target_university: e.target.value })}
              required
            />
          </label>
          <label className="gb-field">
            <span>Target city (US)</span>
            <input value={form.target_city} onChange={(e) => setForm({ ...form, target_city: e.target.value })} required />
          </label>

          <fieldset className="gb-field gb-field--full gb-radio-fieldset">
            <legend>Are you new to the US?</legend>
            <div className="gb-radio-row" role="radiogroup" aria-label="Are you new to the US?">
              <label>
                <input
                  type="radio"
                  name="new_to_us"
                  checked={form.new_to_us === true}
                  onChange={() => setForm({ ...form, new_to_us: true })}
                />
                Yes, I am new
              </label>
              <label>
                <input
                  type="radio"
                  name="new_to_us"
                  checked={form.new_to_us === false}
                  onChange={() => setForm({ ...form, new_to_us: false })}
                />
                No, I have lived in the US before
              </label>
            </div>
          </fieldset>

          <label className="gb-field gb-field--full">
            <span>Needs (comma-separated)</span>
            <input
              value={form.needs}
              onChange={(e) => setForm({ ...form, needs: e.target.value })}
              placeholder="banking, housing, orientation"
            />
          </label>
          <label className="gb-field gb-field--full">
            <span>Interests (comma-separated)</span>
            <input value={form.interests} onChange={(e) => setForm({ ...form, interests: e.target.value })} />
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
              placeholder="Hindu, Muslim, Sikh"
            />
          </label>
          <label className="gb-field">
            <span>Diet (optional)</span>
            <input
              value={form.diet}
              onChange={(e) => setForm({ ...form, diet: e.target.value })}
              placeholder="vegetarian, halal"
            />
          </label>
          <label className="gb-field gb-field--full">
            <span>LinkedIn (optional)</span>
            <input
              value={form.linkedin_url}
              onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })}
              placeholder="https://www.linkedin.com/in/your-profile"
            />
          </label>
          <label className="gb-field">
            <span>Instagram (optional)</span>
            <input
              value={form.instagram_url}
              onChange={(e) => setForm({ ...form, instagram_url: e.target.value })}
              placeholder="@yourhandle or profile URL"
            />
          </label>
          <label className="gb-field">
            <span>Other social (optional)</span>
            <input
              value={form.other_social_url}
              onChange={(e) => setForm({ ...form, other_social_url: e.target.value })}
              placeholder="Any other social profile"
            />
          </label>
        </div>
        <div style={{ marginTop: "1.15rem" }} className="gb-profile-submit">
          <button type="submit" className="gb-btn gb-btn-primary gb-btn-full" disabled={loading}>
            {loading ? "Saving profile and matching graph..." : "Save profile and continue"}
          </button>
        </div>
      </form>
      {error && <div className="gb-error">{typeof error === "string" ? error : JSON.stringify(error)}</div>}
    </section>
  );
}
