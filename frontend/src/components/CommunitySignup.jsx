import { useEffect, useState } from "react";

const STORAGE_KEY = "globalbuddy_student_profile_v1";

/**
 * Lightweight local “join” for the hackathon demo — not a full auth system.
 * Saves name + email in localStorage so you can narrate “students opt in, then we match from the graph.”
 * Production would use accounts + verified emails in Neo4j.
 */
export default function CommunitySignup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [saved, setSaved] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const j = JSON.parse(raw);
        setName(j.display_name || "");
        setEmail(j.email || "");
        setSaved(Boolean(j.display_name && j.email));
      }
    } catch {
      /* ignore */
    }
    setLoaded(true);
  }, []);

  function save(e) {
    e.preventDefault();
    const payload = {
      display_name: name.trim(),
      email: email.trim(),
      saved_at: new Date().toISOString(),
    };
    if (!payload.display_name || !payload.email) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    setSaved(true);
  }

  function clearSaved() {
    localStorage.removeItem(STORAGE_KEY);
    setName("");
    setEmail("");
    setSaved(false);
  }

  if (!loaded) return null;

  return (
    <section className="gb-card gb-community-card">
      <h2 className="gb-card-title--plain">Join your cohort (demo)</h2>
      <p style={{ margin: "0 0 1rem", color: "var(--gb-muted)", fontSize: "0.88rem", lineHeight: 1.5 }}>
        Full registration and verified profiles would live in the product backend. For this build, save your name and
        email <strong style={{ color: "var(--gb-text)" }}>locally in this browser</strong> to simulate “I’m on the
        platform” before you run a graph match. Later, the same fields would sync to Postgres + Neo4j after email
        verification.
      </p>
      {saved ? (
        <div className="gb-community-saved">
          <p style={{ margin: 0, fontSize: "0.9rem" }}>
            Saved for this browser: <strong>{name}</strong> · <code style={{ color: "var(--gb-accent)" }}>{email}</code>
          </p>
          <button type="button" className="gb-btn gb-btn-secondary" style={{ marginTop: "0.65rem", fontSize: "0.85rem" }} onClick={clearSaved}>
            Clear saved profile
          </button>
        </div>
      ) : (
        <form className="gb-community-form" onSubmit={save}>
          <label className="gb-field gb-field--full">
            <span>Display name</span>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Priya" autoComplete="name" required />
          </label>
          <label className="gb-field gb-field--full">
            <span>Email</span>
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="you@university.edu" autoComplete="email" required />
          </label>
          <button type="submit" className="gb-btn gb-btn-primary" style={{ marginTop: "0.35rem" }}>
            Save locally (demo opt-in)
          </button>
        </form>
      )}
    </section>
  );
}
