const LABELS = {
  student: "You",
  mentor: "Mentor",
  peer: "Peer",
  restaurant: "Restaurant",
  event: "Event",
  resource: "Resource",
  task: "Task",
};

export default function NodeDetailCard({ node, onClear }) {
  if (!node) return null;
  const kind = LABELS[node.group] || node.group || "Node";
  return (
    <div className="gb-node-detail">
      <div className="gb-node-detail__type">{kind}</div>
      <div style={{ fontWeight: 600, marginBottom: "0.35rem" }}>{node.label}</div>
      {node.subtitle && <div style={{ color: "var(--gb-muted)", fontSize: "0.85rem" }}>{node.subtitle}</div>}
      {onClear && (
        <button type="button" className="gb-btn gb-btn-secondary" style={{ marginTop: "0.75rem", padding: "0.45rem 0.85rem", fontSize: "0.82rem" }} onClick={onClear}>
          Clear selection
        </button>
      )}
    </div>
  );
}
