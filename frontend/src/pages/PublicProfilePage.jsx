import { Link, useParams } from "react-router-dom";

export default function PublicProfilePage() {
  const { id } = useParams();

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalà¤¦à¥‹à¤¸à¥à¤¤"}</span>
        </Link>
        <div className="gb-nav-right">
          <Link to="/dashboard" className="gb-btn gb-btn-ghost">Dashboard</Link>
        </div>
      </nav>

      <main className="gb-main">
        <section className="gb-card gb-dash-hero">
          <p className="gb-hero-kicker">Community profile</p>
          <h1>Profile {id}</h1>
          <p style={{ color: "var(--gb-muted)", margin: 0 }}>
            Mentor details, connection status, and ratings will appear here as the community graph fills in.
          </p>
        </section>
      </main>
    </div>
  );
}
