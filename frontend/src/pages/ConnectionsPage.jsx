import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import client from "../api/client.js";
import { useAuth } from "../contexts/AuthContext.jsx";

const KIND_LABELS = {
  connection: "Connection",
  intro: "Mentor intro",
};

const STATUS_LABELS = {
  pending: "Pending",
  accepted: "Accepted",
  declined: "Declined",
};

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export default function ConnectionsPage() {
  const { user, accessToken, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user || !accessToken) {
      navigate("/auth");
      return;
    }
    let cancelled = false;
    client
      .get("/v1/social/requests")
      .then((r) => {
        if (!cancelled) setItems(r.data.items || []);
      })
      .catch((e) => {
        if (!cancelled) setError(e.response?.data?.detail || "Could not load your connections.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [authLoading, user, accessToken, navigate]);

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
        <div className="gb-nav-right">
          <Link to="/dashboard" className="gb-btn gb-btn-ghost">Dashboard</Link>
        </div>
      </nav>

      <div className="gb-main">
        <header className="gb-card gb-dash-hero">
          <p className="gb-hero-kicker">Your network</p>
          <h1>My Connections</h1>
          <p style={{ color: "var(--gb-muted)", margin: 0 }}>
            Connection and mentor-intro requests you've sent. Mentor intros are emailed on your behalf — their address stays private.
          </p>
        </header>

        {loading ? (
          <div className="gb-card" style={{ padding: "2rem", textAlign: "center", color: "var(--gb-muted)" }}>
            Loading your connections…
          </div>
        ) : error ? (
          <div className="gb-error">{error}</div>
        ) : items.length === 0 ? (
          <div className="gb-card" style={{ padding: "2rem", textAlign: "center" }}>
            <p style={{ color: "var(--gb-muted)", marginBottom: "1rem" }}>
              You haven't sent any requests yet. Open Explore and reach out to a mentor or peer.
            </p>
            <Link to="/dashboard" className="gb-btn gb-btn-primary">Back to dashboard</Link>
          </div>
        ) : (
          <ul className="gb-connections-list">
            {items.map((item) => (
              <li key={item.id} className="gb-card gb-connection-item">
                <div className="gb-connection-item__main">
                  <span className={`gb-badge gb-badge--${item.kind === "intro" ? "accent" : "muted"}`}>
                    {KIND_LABELS[item.kind] || item.kind}
                  </span>
                  <strong>{item.target_name || item.target_node_id}</strong>
                  {item.target_role && <span className="gb-connection-item__role">{item.target_role}</span>}
                </div>
                <div className="gb-connection-item__meta">
                  <span className={`gb-status-pill gb-status-pill--${item.status}`}>
                    {STATUS_LABELS[item.status] || item.status}
                  </span>
                  {item.kind === "intro" && (
                    <span className="gb-connection-item__email">
                      {item.email_sent ? "Email sent" : "Email pending"}
                    </span>
                  )}
                  <span className="gb-connection-item__date">{formatDate(item.created_at)}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
