import MapPreviewPanel from "./MapPreviewPanel.jsx";

function openMapsUrl(item) {
  const u = (item.maps_link || "").trim();
  if (u) return u;
  const q = (item.maps_query || item.name || "").trim();
  if (!q) return "";
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}`;
}

function LocalRow({ item, badge }) {
  const href = openMapsUrl(item);
  return (
    <article className="gb-local-card">
      <div className="gb-local-card__head">
        <span className="gb-local-badge">{badge}</span>
        <div className="gb-local-card__title">{item.name}</div>
      </div>
      {item.neighborhood && <div className="gb-local-meta">{item.neighborhood}</div>}
      {item.address && <div className="gb-local-meta">{item.address}</div>}
      {item.why_recommended && (
        <p className="gb-local-why">
          <strong>Why recommended</strong> | {item.why_recommended}
        </p>
      )}
      <div className="gb-local-actions">
        {href && (
          <a className="gb-btn gb-btn-primary gb-local-btn" href={href} target="_blank" rel="noopener noreferrer">
            Open in Google Maps
          </a>
        )}
      </div>
      <MapPreviewPanel mapsLink={item.maps_link} mapsQuery={item.maps_query} title={item.name} />
    </article>
  );
}

function TransitRow({ t }) {
  const href = openMapsUrl(t);
  return (
    <article className="gb-local-card gb-local-card--transit">
      <div className="gb-local-card__head">
        <span className="gb-local-badge gb-local-badge--transit">Transit</span>
        <div className="gb-local-card__title">{t.name}</div>
      </div>
      {t.summary && <p className="gb-local-why">{t.summary}</p>}
      {t.route_hint && (
        <p className="gb-local-meta" style={{ fontSize: "0.82rem", lineHeight: 1.45 }}>
          <strong>Route hint</strong> | {t.route_hint}
        </p>
      )}
      {href && (
        <div className="gb-local-actions">
          <a className="gb-btn gb-btn-secondary gb-local-btn" href={href} target="_blank" rel="noopener noreferrer">
            Open in Google Maps
          </a>
        </div>
      )}
    </article>
  );
}

function EventRow({ e }) {
  const href = openMapsUrl(e);
  return (
    <article className="gb-local-card">
      <div className="gb-local-card__head">
        <span className="gb-local-badge gb-local-badge--event">Event</span>
        <div className="gb-local-card__title">{e.name}</div>
      </div>
      <div className="gb-local-meta">
        {e.category}
        {e.start_time ? ` | ${e.start_time}` : ""}
      </div>
      {e.location && <div className="gb-local-meta">{e.location}</div>}
      {e.notes && (
        <p className="gb-local-why">
          <strong>Note</strong> | {e.notes}
        </p>
      )}
      {href && (
        <div className="gb-local-actions">
          <a className="gb-btn gb-btn-primary gb-local-btn" href={href} target="_blank" rel="noopener noreferrer">
            Open in Google Maps
          </a>
        </div>
      )}
      <MapPreviewPanel mapsLink={e.maps_link} mapsQuery={e.maps_query} title={e.name} />
    </article>
  );
}

function ResourceRow({ resource }) {
  return (
    <article className="gb-local-card">
      <div className="gb-local-card__head">
        <span className="gb-local-badge gb-local-badge--resource">Resource</span>
        <div className="gb-local-card__title">{resource.name}</div>
      </div>
      <div className="gb-local-meta">{resource.resource_type || "General support"}</div>
    </article>
  );
}

export default function CommunityFitPanel({ match }) {
  if (!match) return null;

  const worship = match.places_of_worship || [];
  const groceries = match.grocery_stores || [];
  const housing = match.housing_areas || [];
  const explore = match.exploration_spots || [];
  const transit = match.transit_tips || [];
  const resources = match.resources || [];
  const events = (match.community_events || []).filter(
    (e) => e.notes || e.category === "religious_cultural" || e.category === "seasonal_cultural",
  );

  const hasLocal =
    worship.length + groceries.length + housing.length + explore.length + transit.length + resources.length > 0;

  if (!hasLocal && events.length === 0 && !match.best_weekend_outing) {
    return null;
  }

  return (
    <section className="gb-card gb-community" aria-label="Explore nearby">
      <h2 className="gb-card-title--plain">Explore mode: nearby in your city</h2>
      <p className="gb-community__lede">
        Graph-grounded nearby context for people, events, places, transit, and resources. Dates and routes are not live,
        so verify with official sources.
      </p>
      {(match.cultural_fit_score != null || match.best_weekend_outing) && (
        <div className="gb-community__scores">
          {match.cultural_fit_score != null && (
            <span className="gb-community__pill">
              Cultural fit (graph tags): <strong>{Math.round(Number(match.cultural_fit_score) * 100)}%</strong>
            </span>
          )}
          {match.best_weekend_outing && (
            <div className="gb-weekend-suggestion">
              <span className="gb-weekend-suggestion__label">Weekend comfort</span>
              {match.best_weekend_outing}
            </div>
          )}
        </div>
      )}

      {worship.length > 0 && (
        <div className="gb-community__block">
          <h3 className="gb-community__h">Community and worship</h3>
          <div className="gb-local-stack">
            {worship.map((p) => (
              <LocalRow key={p.id} item={p} badge="Worship" />
            ))}
          </div>
        </div>
      )}

      {events.length > 0 && (
        <div className="gb-community__block">
          <h3 className="gb-community__h">Cultural and religious events</h3>
          <div className="gb-local-stack">
            {events.map((e) => (
              <EventRow key={e.id} e={e} />
            ))}
          </div>
        </div>
      )}

      {resources.length > 0 && (
        <div className="gb-community__block">
          <h3 className="gb-community__h">Resources</h3>
          <div className="gb-local-stack">
            {resources.map((resource) => (
              <ResourceRow key={resource.id} resource={resource} />
            ))}
          </div>
        </div>
      )}

      {explore.length > 0 && (
        <div className="gb-community__block">
          <h3 className="gb-community__h">Places to visit</h3>
          <div className="gb-local-stack">
            {explore.map((p) => (
              <LocalRow key={p.id} item={p} badge="Explore" />
            ))}
          </div>
        </div>
      )}

      {groceries.length > 0 && (
        <div className="gb-community__block">
          <h3 className="gb-community__h">Groceries and essentials</h3>
          <div className="gb-local-stack">
            {groceries.map((p) => (
              <LocalRow key={p.id} item={p} badge="Grocery" />
            ))}
          </div>
        </div>
      )}

      {housing.length > 0 && (
        <div className="gb-community__block">
          <h3 className="gb-community__h">Housing areas</h3>
          <div className="gb-local-stack">
            {housing.map((p) => (
              <LocalRow key={p.id} item={p} badge="Housing" />
            ))}
          </div>
        </div>
      )}

      {transit.length > 0 && (
        <div className="gb-community__block">
          <h3 className="gb-community__h">Getting around</h3>
          <div className="gb-local-stack">
            {transit.map((t) => (
              <TransitRow key={t.id} t={t} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
