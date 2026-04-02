import { useState } from "react";

function pct(n) {
  if (n == null || Number.isNaN(Number(n))) return "—";
  return `${Math.round(Number(n) * 100)}%`;
}

function ConnectRow({ email, linkedinUrl, name }) {
  const [copied, setCopied] = useState(false);

  async function copyEmail() {
    if (!email) return;
    try {
      await navigator.clipboard.writeText(email);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  if (!email && !linkedinUrl) return null;

  return (
    <div className="gb-match-connect">
      <div className="gb-match-connect__label">Connect</div>
      <div className="gb-match-connect__actions">
        {email && (
          <>
            <a className="gb-btn gb-btn-primary gb-match-connect__btn" href={`mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(`GlobalBuddy intro — ${name}`)}`}>
              Email
            </a>
            <button type="button" className="gb-btn gb-btn-secondary gb-match-connect__btn" onClick={copyEmail}>
              {copied ? "Copied" : "Copy email"}
            </button>
            <span className="gb-match-connect__email" title={email}>
              {email}
            </span>
          </>
        )}
        {linkedinUrl?.trim() && (
          <a className="gb-link-out" href={linkedinUrl} target="_blank" rel="noopener noreferrer">
            LinkedIn profile
          </a>
        )}
      </div>
    </div>
  );
}

export default function MatchCards({ match }) {
  if (!match) {
    return (
      <section className="gb-card" aria-live="polite">
        <h2 className="gb-card-title--plain">Matches & coverage</h2>
        <p style={{ margin: 0, color: "var(--gb-muted)", fontSize: "0.9rem" }}>
          Run a graph match to see mentors ranked from Neo4j, peer proximity, and coverage scores derived from your
          evidence. Contact details come from the graph when mentors and peers opt in (seed/demo data for the hackathon).
        </p>
      </section>
    );
  }

  const mentors = match.mentors_top3 || [];
  const peers = match.peers_nearby || [];

  return (
    <section className="gb-card" aria-live="polite">
      <h2 className="gb-card-title--plain">Matches & coverage</h2>
      <p style={{ margin: "0 0 1rem", color: "var(--gb-muted)", fontSize: "0.88rem" }}>
        Top mentors from the graph with deterministic confidence. Support coverage reflects how well resources and
        mentors align with your stated needs; belonging blends peers, events, food, and mentor links.{" "}
        <strong style={{ color: "var(--gb-text)", fontWeight: 600 }}>Emails and hints are stored in Neo4j</strong> — in
        production, only verified members would appear here.
      </p>
      <div className="gb-score-row">
        <span>
          Support coverage: <strong>{pct(match.support_coverage_score)}</strong>
        </span>
        <span>
          Belonging score: <strong>{pct(match.belonging_score)}</strong>
        </span>
        <span>
          Cultural fit: <strong>{pct(match.cultural_fit_score)}</strong>
        </span>
      </div>
      {mentors.length === 0 ? (
        <p style={{ margin: 0, color: "var(--gb-muted)", fontSize: "0.9rem" }}>No mentor nodes matched this profile yet.</p>
      ) : (
        <div className="gb-match-stack">
          <h3 className="gb-match-section-title">Mentors</h3>
          {mentors.map((m) => (
            <article key={m.id} className="gb-match-card">
              <div className="gb-match-card__head">
                <div>
                  <div style={{ fontWeight: 600 }}>{m.name}</div>
                  <div style={{ fontSize: "0.8rem", color: "var(--gb-muted)", marginTop: "0.2rem" }}>
                    {(m.match_reasons || []).join(" · ") || "Graph-ranked match"}
                  </div>
                </div>
                <span className="gb-badge" title="Confidence from graph match score">
                  {pct(m.confidence_score ?? m.match_score)} conf.
                </span>
              </div>
              {m.why_this_match && (
                <p style={{ margin: "0 0 0.75rem", fontSize: "0.88rem", color: "var(--gb-text)", lineHeight: 1.45 }}>
                  <strong style={{ color: "var(--gb-accent)" }}>Why this match?</strong> {m.why_this_match}
                </p>
              )}
              {m.connect_hint && (
                <p className="gb-match-hint">
                  <strong>How to reach out</strong> — {m.connect_hint}
                </p>
              )}
              <ConnectRow email={m.email} linkedinUrl={m.linkedin_url} name={m.name} />
            </article>
          ))}
        </div>
      )}

      {peers.length > 0 && (
        <div className="gb-match-stack" style={{ marginTop: "1.25rem" }}>
          <h3 className="gb-match-section-title">Peers nearby</h3>
          {peers.map((p) => (
            <article key={p.id} className="gb-match-card gb-match-card--peer">
              <div className="gb-match-card__head">
                <div>
                  <div style={{ fontWeight: 600 }}>{p.name}</div>
                  <div style={{ fontSize: "0.8rem", color: "var(--gb-muted)", marginTop: "0.2rem" }}>
                    {p.neighborhood} · {p.university}
                  </div>
                </div>
              </div>
              {p.connect_hint && (
                <p className="gb-match-hint">
                  <strong>How to connect</strong> — {p.connect_hint}
                </p>
              )}
              <ConnectRow email={p.email} linkedinUrl="" name={p.name} />
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
