import MapPreviewPanel from "./MapPreviewPanel.jsx";

const LABELS = {
  student: "You",
  mentor: "Mentor",
  peer: "Peer",
  restaurant: "Restaurant",
  event: "Event",
  resource: "Resource",
  task: "Task",
  place_worship: "Community or worship",
  grocery: "Grocery",
  housing_area: "Housing area",
  exploration: "Place to explore",
  transit_tip: "Transit tip",
};

function mapsHref(node) {
  const direct = (node?.maps_link || "").trim();
  if (direct) return direct;

  const query = (node?.maps_query || node?.address || node?.label || "").trim();
  if (!query) return "";

  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

export default function NodeDetailCard({ node, onClear }) {
  if (!node) return null;

  const kind = LABELS[node.group] || node.group || "Node";
  const href = mapsHref(node);

  return (
    <div className="gb-node-detail gb-node-detail--rich">
      <div className="gb-node-detail__row">
        <span className="gb-node-detail__type">{kind}</span>
        {node.subtitle && <span className="gb-node-detail__chip">{node.subtitle}</span>}
      </div>

      <h4 className="gb-node-detail__title">{node.label}</h4>

      {node.address && <div className="gb-node-detail__address">{node.address}</div>}

      {node.why_recommended && (
        <div className="gb-node-detail__why-block">
          <strong>Why this match?</strong>
          <p>{node.why_recommended}</p>
        </div>
      )}

      <div className="gb-node-detail__actions">
        {href && (
          <a className="gb-btn gb-btn-primary" href={href} target="_blank" rel="noopener noreferrer">
            Open in Google Maps
          </a>
        )}

        {onClear && (
          <button type="button" className="gb-btn gb-btn-secondary" onClick={onClear}>
            Clear selection
          </button>
        )}
      </div>

      <MapPreviewPanel mapsLink={node.maps_link} mapsQuery={node.maps_query} title={node.label} />
    </div>
  );
}
