import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client.js";
import { useAuth } from "../contexts/AuthContext.jsx";

const CATEGORIES = [
  { id: "", label: "All" },
  { id: "guide", label: "Guides" },
  { id: "event", label: "Events" },
  { id: "food", label: "Food" },
  { id: "tip", label: "Tips" },
];

const TYPE_LABELS = { guide: "Guide", event: "Event", food: "Food", tip: "Tip" };

function osmHref(item) {
  if (item.maps_link) return item.maps_link;
  const q = (item.maps_query || item.title || "").trim();
  return q ? `https://www.openstreetmap.org/search?query=${encodeURIComponent(q)}` : "";
}

export default function FeedPage({ savedOnly = false }) {
  const { user, accessToken } = useAuth();
  const canSave = Boolean(user && accessToken);

  const [items, setItems] = useState([]);
  const [category, setCategory] = useState("");
  const [offset, setOffset] = useState(0);
  const [nextOffset, setNextOffset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [savedIds, setSavedIds] = useState(() => new Set());

  const load = useCallback(
    async (nextCategory, nextOffsetValue) => {
      setLoading(true);
      setError(null);
      try {
        if (savedOnly) {
          const res = await client.get("/v1/feed/saved");
          setItems(res.data.items || []);
          setNextOffset(null);
          setSavedIds(new Set((res.data.items || []).map((i) => i.id)));
        } else {
          const res = await client.get("/v1/feed", {
            params: { city: "Chicago", category: nextCategory, offset: nextOffsetValue, limit: 9 },
          });
          const incoming = res.data.items || [];
          setItems((prev) => (nextOffsetValue === 0 ? incoming : [...prev, ...incoming]));
          setNextOffset(res.data.next_offset);
          setSavedIds((prev) => {
            const next = new Set(prev);
            incoming.forEach((i) => (i.saved ? next.add(i.id) : null));
            return next;
          });
        }
      } catch (e) {
        setError(e.response?.data?.detail || "Could not load the feed.");
      } finally {
        setLoading(false);
      }
    },
    [savedOnly]
  );

  useEffect(() => {
    setOffset(0);
    load(category, 0);
  }, [category, load]);

  const loadMore = () => {
    if (nextOffset == null) return;
    setOffset(nextOffset);
    load(category, nextOffset);
  };

  const toggleSave = async (item) => {
    if (!canSave) return;
    const isSaved = savedIds.has(item.id);
    // Optimistic update.
    setSavedIds((prev) => {
      const next = new Set(prev);
      isSaved ? next.delete(item.id) : next.add(item.id);
      return next;
    });
    try {
      if (isSaved) {
        await client.delete(`/v1/feed/save/${encodeURIComponent(item.id)}`, {
          params: { content_source: item.source },
        });
        if (savedOnly) setItems((prev) => prev.filter((i) => i.id !== item.id));
      } else {
        await client.post("/v1/feed/save", { content_id: item.id, content_source: item.source });
      }
    } catch {
      // Revert on failure.
      setSavedIds((prev) => {
        const next = new Set(prev);
        isSaved ? next.add(item.id) : next.delete(item.id);
        return next;
      });
    }
  };

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
        <div className="gb-nav-right">
          {!savedOnly && canSave && <Link to="/saved" className="gb-btn gb-btn-ghost">Saved</Link>}
          <Link to="/dashboard" className="gb-btn gb-btn-ghost">Dashboard</Link>
        </div>
      </nav>

      <div className="gb-main">
        <header className="gb-card gb-dash-hero">
          <p className="gb-hero-kicker">{savedOnly ? "Your library" : "Discover your city"}</p>
          <h1>{savedOnly ? "Saved" : "Chicago Feed"}</h1>
          <p style={{ color: "var(--gb-muted)", margin: 0 }}>
            {savedOnly
              ? "Guides, events, and tips you've saved for later."
              : "Guides, events, food spotlights, and tips for settling into Chicago — beyond your 30-day plan."}
          </p>
        </header>

        {!savedOnly && (
          <div className="gb-pa-tabs" role="tablist">
            {CATEGORIES.map((c) => (
              <button
                key={c.id || "all"}
                role="tab"
                aria-selected={category === c.id}
                className={`gb-pa-tab ${category === c.id ? "gb-pa-tab--active" : ""}`}
                onClick={() => setCategory(c.id)}
              >
                {c.label}
              </button>
            ))}
          </div>
        )}

        {error && <div className="gb-error">{error}</div>}

        {loading && items.length === 0 ? (
          <div className="gb-card" style={{ padding: "2rem", textAlign: "center", color: "var(--gb-muted)" }}>
            Loading feed…
          </div>
        ) : items.length === 0 ? (
          <div className="gb-card" style={{ padding: "2rem", textAlign: "center", color: "var(--gb-muted)" }}>
            {savedOnly ? "You haven't saved anything yet." : "No items in this category yet."}
          </div>
        ) : (
          <div className="gb-feed-grid">
            {items.map((item) => {
              const href = osmHref(item);
              const isSaved = savedIds.has(item.id);
              return (
                <article key={`${item.source}-${item.id}`} className="gb-card gb-feed-card">
                  <div className="gb-feed-card__head">
                    <span className="gb-badge">{TYPE_LABELS[item.type] || item.type}</span>
                    {canSave && (
                      <button
                        type="button"
                        className={`gb-feed-save ${isSaved ? "gb-feed-save--on" : ""}`}
                        onClick={() => toggleSave(item)}
                        aria-pressed={isSaved}
                        aria-label={isSaved ? "Unsave" : "Save"}
                      >
                        {isSaved ? "★ Saved" : "☆ Save"}
                      </button>
                    )}
                  </div>
                  <h3 className="gb-feed-card__title">{item.title}</h3>
                  {item.body && <p className="gb-feed-card__body">{item.body}</p>}
                  <div className="gb-feed-card__footer">
                    {item.tags?.slice(0, 3).map((tag) => (
                      <span key={tag} className="gb-chip gb-chip--soft">{tag}</span>
                    ))}
                    {href && (
                      <a className="gb-link-btn" href={href} target="_blank" rel="noopener noreferrer">
                        OpenStreetMap
                      </a>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        )}

        {!savedOnly && nextOffset != null && (
          <div style={{ textAlign: "center", marginTop: "1.25rem" }}>
            <button type="button" className="gb-btn gb-btn-secondary" onClick={loadMore} disabled={loading}>
              {loading ? "Loading…" : "Load more"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
