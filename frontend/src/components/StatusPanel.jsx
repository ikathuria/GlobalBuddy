import { useEffect, useState } from "react";
import client, { API_BASE_URL } from "../api/client.js";

function normalizeHealthBody(data) {
  if (data == null) return null;
  if (typeof data === "string") {
    try {
      return JSON.parse(data);
    } catch {
      return null;
    }
  }
  return data;
}

export default function StatusPanel({ compact = false }) {
  const [apiLabel, setApiLabel] = useState("checking...");
  const [apiOk, setApiOk] = useState(null);
  const [neo4j, setNeo4j] = useState(null);
  const [neo4jError, setNeo4jError] = useState(null);
  const [tick, setTick] = useState(0);
  const [apiError, setApiError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setApiLabel("checking...");
    setApiOk(null);
    setApiError(null);
    setNeo4jError(null);

    const run = async () => {
      const healthP = client.get("/health");
      const neo4jP = client.get("/health/neo4j");
      const [healthSettled, neo4jSettled] = await Promise.allSettled([healthP, neo4jP]);

      if (cancelled) return;

      if (healthSettled.status === "fulfilled") {
        const r = healthSettled.value;
        const body = normalizeHealthBody(r.data);
        const statusField = body?.status;
        const looksOk = r.status === 200 && String(statusField ?? "").toLowerCase() === "ok";
        setApiOk(looksOk);
        setApiLabel(looksOk ? "live" : `HTTP ${r.status}`);
        if (!looksOk) {
          setApiError(
            statusField === undefined
              ? "Health returned 200 but no status=ok."
              : `Unexpected health payload: ${JSON.stringify(body)}`,
          );
        }
      } else {
        const e = healthSettled.reason;
        setApiOk(false);
        setApiLabel("offline");
        const msg =
          e?.code === "ERR_NETWORK"
            ? "Network error (port/CORS/server issue)."
            : e?.response?.status
              ? `HTTP ${e.response.status}`
              : e?.message || "error";
        setApiError(msg);
      }

      if (neo4jSettled.status === "fulfilled") {
        setNeo4j(neo4jSettled.value.data);
        setNeo4jError(null);
      } else {
        const e = neo4jSettled.reason;
        setNeo4j(null);
        setNeo4jError(e?.message || "Neo4j probe failed");
      }
    };

    run();
    return () => {
      cancelled = true;
    };
  }, [tick]);

  const row = (
    <div className={`gb-status-row ${compact ? "gb-status-row--inline" : ""}`}>
      <span className={`gb-pill ${apiOk === true ? "gb-pill--ok" : apiOk === false ? "gb-pill--bad" : ""}`}>
        <span className="gb-pill-dot" aria-hidden="true" />
        API {apiOk === true ? "live" : apiOk === false ? "offline" : apiLabel}
      </span>
      {neo4j && !neo4jError && (
        <span className="gb-pill">
          <span className="gb-pill-dot" style={{ color: "var(--gb-accent)" }} aria-hidden="true" />
          Neo4j | {neo4j.node_count ?? "?"} nodes
        </span>
      )}
      {neo4jError && (
        <span className="gb-pill gb-pill--bad" title={neo4jError}>
          <span className="gb-pill-dot" aria-hidden="true" />
          Neo4j issue
        </span>
      )}
      {!compact && (
        <button
          type="button"
          className="gb-btn gb-btn-secondary"
          style={{ padding: "0.45rem 0.85rem", fontSize: "0.82rem" }}
          onClick={() => setTick((t) => t + 1)}
        >
          Retry check
        </button>
      )}
    </div>
  );

  if (compact) {
    return (
      <div className="gb-status-inline" aria-label="Health checks" title={apiError || neo4jError || "Health checks"}>
        {row}
      </div>
    );
  }

  return (
    <section className="gb-card">
      <h2>System status</h2>
      {row}
      {apiOk === false && apiError && (
        <p
          className="gb-seed-hint"
          style={{ marginTop: "0.75rem", borderColor: "var(--gb-border)", background: "rgba(148,163,184,0.06)", color: "var(--gb-muted)" }}
        >
          <strong style={{ color: "var(--gb-text)" }}>Calling</strong> <code style={{ color: "var(--gb-accent)" }}>{API_BASE_URL}</code>
          <br />
          <span style={{ fontSize: "0.82rem" }}>{apiError}</span>
        </p>
      )}
      {neo4j?.node_count === 0 && neo4j.seed_command && (
        <p className="gb-seed-hint">
          Graph is empty. Seed once so matches return real evidence.
          <code>{neo4j.seed_command}</code>
        </p>
      )}
    </section>
  );
}
