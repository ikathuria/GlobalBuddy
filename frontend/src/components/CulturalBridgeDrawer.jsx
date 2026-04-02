import { useEffect } from "react";

export default function CulturalBridgeDrawer({ open, onClose, bridge, loading, error, onRetry }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") onClose?.();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="gb-drawer-backdrop" role="presentation" onMouseDown={(e) => e.target === e.currentTarget && onClose?.()}>
      <aside className="gb-drawer" role="dialog" aria-modal="true" aria-labelledby="bridge-drawer-title" onMouseDown={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.75rem" }}>
          <h2 id="bridge-drawer-title">Cultural bridge</h2>
          <button type="button" className="gb-banner__close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>
        <p style={{ margin: "0 0 1rem", color: "var(--gb-muted)", fontSize: "0.88rem" }}>
          US-term explanations grounded in your home context — not open-ended chat. Click a highlighted term in the plan
          or use Explain term.
        </p>
        {loading && (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.65rem" }}>
            <div className="gb-skeleton" style={{ height: 28 }} />
            <div className="gb-skeleton" style={{ height: 80 }} />
            <div className="gb-skeleton" style={{ height: 60 }} />
          </div>
        )}
        {error && !loading && (
          <div>
            <div className="gb-error" style={{ marginTop: 0 }}>
              {typeof error === "string" ? error : JSON.stringify(error)}
            </div>
            {onRetry && (
              <button type="button" className="gb-btn gb-btn-secondary" style={{ marginTop: "0.75rem" }} onClick={onRetry}>
                Retry
              </button>
            )}
          </div>
        )}
        {!loading && !error && bridge && (
          <div>
            <h3 style={{ margin: "0 0 0.5rem", fontSize: "1.15rem" }}>{bridge.term}</h3>
            <p style={{ lineHeight: 1.55 }}>{bridge.plain_explanation}</p>
            <p style={{ color: "var(--gb-muted)", marginTop: "1rem" }}>
              <em style={{ color: "var(--gb-accent)", fontStyle: "normal", fontWeight: 600 }}>Home context</em> —{" "}
              {bridge.home_context_analogy}
            </p>
            {(bridge.common_mistakes || []).length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <div style={{ fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--gb-muted)" }}>
                  Common mistakes
                </div>
                <ul style={{ margin: "0.4rem 0 0", paddingLeft: "1.1rem", color: "var(--gb-text)", fontSize: "0.9rem" }}>
                  {bridge.common_mistakes.map((x, i) => (
                    <li key={i}>{x}</li>
                  ))}
                </ul>
              </div>
            )}
            {(bridge.what_to_do_next || []).length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <div style={{ fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--gb-muted)" }}>
                  What to do next
                </div>
                <ul style={{ margin: "0.4rem 0 0", paddingLeft: "1.1rem", color: "var(--gb-text)", fontSize: "0.9rem" }}>
                  {bridge.what_to_do_next.map((x, i) => (
                    <li key={i}>{x}</li>
                  ))}
                </ul>
              </div>
            )}
            <p className="gb-meta" style={{ marginTop: "1rem" }}>
              {bridge.llm_provider} · fallback {String(bridge.fallback_used)}
            </p>
          </div>
        )}
      </aside>
    </div>
  );
}
