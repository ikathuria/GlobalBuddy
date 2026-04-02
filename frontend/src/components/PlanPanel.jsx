import { useState } from "react";
import client from "../api/client.js";
import CulturalBridgeDrawer from "./CulturalBridgeDrawer.jsx";

const QUICK_TERMS = ["security deposit", "credit score", "SSN"];

export default function PlanPanel({ sessionId, matchPayload }) {
  const [plan, setPlan] = useState(null);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [loadingBridge, setLoadingBridge] = useState(false);
  const [planError, setPlanError] = useState(null);
  const [bridgeError, setBridgeError] = useState(null);
  const [term, setTerm] = useState("security deposit");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [bridge, setBridge] = useState(null);

  async function generatePlan() {
    if (!sessionId || !matchPayload?.evidence_bundle) {
      setPlanError("Run profile match first.");
      return;
    }

    setLoadingPlan(true);
    setPlanError(null);

    try {
      const res = await client.post("/v1/plan/generate", {
        session_id: sessionId,
        student_profile: matchPayload.evidence_bundle.student_profile || {},
        evidence_bundle: matchPayload.evidence_bundle,
      });
      setPlan(res.data);
    } catch (err) {
      setPlanError(err.response?.data?.detail || err.message);
    } finally {
      setLoadingPlan(false);
    }
  }

  async function explainTerm(termToUse) {
    const nextTerm = (termToUse ?? term).trim();
    if (!sessionId) {
      setBridgeError("Run profile match first.");
      setDrawerOpen(true);
      return;
    }
    if (!nextTerm) return;

    setLoadingBridge(true);
    setBridgeError(null);
    setBridge(null);
    setDrawerOpen(true);

    try {
      const res = await client.post("/v1/bridge/explain", {
        session_id: sessionId,
        term: nextTerm,
        home_country: matchPayload?.evidence_bundle?.student_profile?.country_of_origin || "India",
        context: "off-campus rental and banking setup",
      });
      setBridge(res.data);
      setTerm(nextTerm);
    } catch (err) {
      setBridgeError(err.response?.data?.detail || err.message);
    } finally {
      setLoadingBridge(false);
    }
  }

  function retryBridge() {
    explainTerm(term);
  }

  return (
    <>
      <section className="gb-card">
        <h2>Survival plan and cultural bridge</h2>
        <p style={{ margin: "0 0 1rem", color: "var(--gb-muted)", fontSize: "0.9rem" }}>
          Keep this focused and fast: decode a US term first, then generate your 30-day plan from graph evidence.
        </p>

        <h3 className="gb-card-title--plain" style={{ marginBottom: "0.5rem" }}>
          Explain a US term
        </h3>
        <p style={{ margin: "0 0 0.85rem", color: "var(--gb-muted)", fontSize: "0.88rem" }}>
          Opens the cultural bridge drawer with a structured explanation.
        </p>

        <div className="gb-actions">
          <input
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            placeholder="e.g. security deposit"
            aria-label="Term to explain"
            disabled={loadingBridge}
          />
          <button
            type="button"
            className="gb-btn gb-btn-secondary"
            onClick={() => explainTerm()}
            disabled={loadingBridge || loadingPlan}
          >
            Explain term
          </button>
        </div>

        <div className="gb-strip" style={{ marginTop: "0.65rem" }}>
          {QUICK_TERMS.map((quickTerm) => (
            <button
              key={quickTerm}
              type="button"
              className="gb-chip"
              style={{ cursor: "pointer", border: "none", font: "inherit" }}
              onClick={() => {
                setTerm(quickTerm);
                explainTerm(quickTerm);
              }}
              disabled={loadingBridge}
            >
              {quickTerm}
            </button>
          ))}
        </div>

        <hr style={{ border: "none", borderTop: "1px solid var(--gb-border)", margin: "1.25rem 0" }} />

        <h3 className="gb-card-title--plain" style={{ marginBottom: "0.5rem" }}>
          Generate your first 30 days
        </h3>
        <p style={{ margin: "0 0 0.85rem", color: "var(--gb-muted)", fontSize: "0.88rem" }}>
          Structured JSON output from your evidence bundle only.
        </p>

        <div className="gb-actions">
          <button
            type="button"
            className="gb-btn gb-btn-primary"
            onClick={generatePlan}
            disabled={loadingPlan || loadingBridge}
          >
            {loadingPlan ? "Generating..." : "Generate my first 30 days"}
          </button>
        </div>

        {loadingPlan && (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.65rem", marginBottom: "1rem" }}>
            <div className="gb-skeleton" style={{ height: 36 }} />
            <div className="gb-skeleton" style={{ height: 72 }} />
            <div className="gb-skeleton" style={{ height: 72 }} />
          </div>
        )}

        {planError && (
          <div className="gb-error" style={{ marginTop: "0.75rem" }}>
            {typeof planError === "string" ? planError : JSON.stringify(planError)}
            <button type="button" className="gb-btn gb-btn-secondary" style={{ marginTop: "0.65rem" }} onClick={generatePlan}>
              Retry
            </button>
          </div>
        )}

        {plan && !loadingPlan && (
          <div>
            {plan.best_next_action && (
              <div className="gb-best-next">
                <div className="gb-best-next__label">Best next action</div>
                <div>{plan.best_next_action}</div>
              </div>
            )}
            <h3 style={{ margin: "0 0 0.5rem", fontSize: "1.05rem" }}>{plan.plan_title}</h3>
            <p className="gb-meta">
              {plan.llm_provider} | fallback {String(plan.fallback_used)} | confidence {plan.confidence}
            </p>
            <div className="gb-steps">
              {(plan.steps || []).map((step, index) => (
                <div key={index} className="gb-step">
                  <div>
                    <strong>{step.day_range}</strong>
                  </div>
                  <div>{step.action}</div>
                  <div className="gb-step-detail">
                    {(step.entities || []).join(" | ")} | {step.dependency_reason}
                  </div>
                </div>
              ))}
            </div>

            {(plan.warnings || []).length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <h3
                  style={{
                    fontSize: "0.85rem",
                    color: "var(--gb-muted)",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                  }}
                >
                  Warnings
                </h3>
                <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.2rem", color: "var(--gb-muted)", fontSize: "0.88rem" }}>
                  {plan.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </section>

      <CulturalBridgeDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        bridge={bridge}
        loading={loadingBridge}
        error={bridgeError}
        onRetry={bridgeError ? retryBridge : undefined}
      />
    </>
  );
}
