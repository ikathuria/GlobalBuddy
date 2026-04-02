import { useEffect, useMemo, useState } from "react";
import client from "../api/client.js";
import CulturalBridgeDrawer from "./CulturalBridgeDrawer.jsx";

const QUICK_TERMS = ["security deposit", "credit score", "SSN"];

function weekLabel(dayRange, index) {
  const values = (String(dayRange || "").match(/\d+/g) || []).map((value) => Number(value));
  const lastDay = values.length ? values[values.length - 1] : (index + 1) * 7;
  const weekNumber = Math.min(4, Math.max(1, Math.ceil(lastDay / 7)));
  return `Week ${weekNumber}`;
}

function stepId(step, index) {
  return `${index}:${step.day_range}:${step.action}`;
}

function storageKey(sessionId) {
  return `gb_plan_progress_${sessionId || "unknown"}`;
}

function readProgress(sessionId) {
  if (!sessionId) return {};
  try {
    const raw = localStorage.getItem(storageKey(sessionId));
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return typeof parsed === "object" && parsed ? parsed : {};
  } catch {
    return {};
  }
}

function saveProgress(sessionId, value) {
  if (!sessionId) return;
  localStorage.setItem(storageKey(sessionId), JSON.stringify(value));
}

export default function PlanPanel({ sessionId, matchPayload, onPlanReady, onFocusNode, onOpenExplore }) {
  const [plan, setPlan] = useState(null);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [loadingBridge, setLoadingBridge] = useState(false);
  const [planError, setPlanError] = useState(null);
  const [bridgeError, setBridgeError] = useState(null);
  const [term, setTerm] = useState("security deposit");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [bridge, setBridge] = useState(null);
  const [expandedStepIds, setExpandedStepIds] = useState({});
  const [completed, setCompleted] = useState(() => readProgress(sessionId));

  useEffect(() => {
    setCompleted(readProgress(sessionId));
  }, [sessionId]);

  useEffect(() => {
    onPlanReady?.(plan);
  }, [plan, onPlanReady]);

  const groupedTimeline = useMemo(() => {
    const groups = new Map();
    (plan?.steps || []).forEach((step, index) => {
      const label = weekLabel(step.day_range, index);
      const existing = groups.get(label) || [];
      existing.push({ step, index, id: stepId(step, index) });
      groups.set(label, existing);
    });
    return Array.from(groups.entries());
  }, [plan?.steps]);

  const completionSummary = useMemo(() => {
    const steps = plan?.steps || [];
    if (!steps.length) return { done: 0, total: 0 };
    const done = steps.reduce((count, step, index) => count + (completed[stepId(step, index)] ? 1 : 0), 0);
    return { done, total: steps.length };
  }, [plan?.steps, completed]);

  async function generatePlan() {
    if (!sessionId || !matchPayload?.evidence_bundle) {
      setPlanError("Complete profile setup first.");
      return;
    }

    setLoadingPlan(true);
    setPlanError(null);

    try {
      const response = await client.post("/v1/plan/generate", {
        session_id: sessionId,
        student_profile: matchPayload.evidence_bundle.student_profile || {},
        evidence_bundle: matchPayload.evidence_bundle,
      });
      setPlan(response.data);
      setExpandedStepIds({});
    } catch (error) {
      setPlanError(error.response?.data?.detail || error.message);
    } finally {
      setLoadingPlan(false);
    }
  }

  async function explainTerm(termToUse) {
    const nextTerm = (termToUse ?? term).trim();
    if (!sessionId) {
      setBridgeError("Complete profile setup first.");
      setDrawerOpen(true);
      return;
    }
    if (!nextTerm) return;

    setLoadingBridge(true);
    setBridgeError(null);
    setBridge(null);
    setDrawerOpen(true);

    try {
      const response = await client.post("/v1/bridge/explain", {
        session_id: sessionId,
        term: nextTerm,
        home_country: matchPayload?.evidence_bundle?.student_profile?.country_of_origin || "India",
        context: "off-campus rental and banking setup",
      });
      setBridge(response.data);
      setTerm(nextTerm);
    } catch (error) {
      setBridgeError(error.response?.data?.detail || error.message);
    } finally {
      setLoadingBridge(false);
    }
  }

  function retryBridge() {
    explainTerm(term);
  }

  function toggleComplete(step, index) {
    const id = stepId(step, index);
    setCompleted((previous) => {
      const next = { ...previous, [id]: !previous[id] };
      saveProgress(sessionId, next);
      return next;
    });
  }

  function toggleExpand(step, index) {
    const id = stepId(step, index);
    setExpandedStepIds((previous) => ({ ...previous, [id]: !previous[id] }));
  }

  return (
    <div className="gb-plan-shell">
      <div className="gb-plan-head">
        <h3>Your First 30 Days Plan</h3>
        <p>
          A calm week-by-week path grounded in your profile and support graph. Mark tasks done as you move forward.
        </p>
      </div>

      <div className="gb-plan-toolbar">
        <button type="button" className="gb-btn gb-btn-primary" onClick={generatePlan} disabled={loadingPlan || loadingBridge}>
          {loadingPlan ? "Building your plan..." : plan ? "Refresh plan" : "Generate my 30-day plan"}
        </button>

        {plan && (
          <button type="button" className="gb-btn gb-btn-secondary" onClick={onOpenExplore}>
            Open graph with plan context
          </button>
        )}
      </div>

      <div className="gb-bridge-box">
        <div className="gb-bridge-box__head">
          <strong>Need clarity on a US term?</strong>
          <span>Use Cultural Bridge for plain-language context before taking action.</span>
        </div>
        <div className="gb-bridge-box__controls">
          <input
            value={term}
            onChange={(event) => setTerm(event.target.value)}
            placeholder="security deposit"
            aria-label="US term to explain"
            disabled={loadingBridge}
          />
          <button
            type="button"
            className="gb-btn gb-btn-secondary"
            onClick={() => explainTerm()}
            disabled={loadingBridge || loadingPlan}
          >
            {loadingBridge ? "Explaining..." : "Explain term"}
          </button>
        </div>
        <div className="gb-chip-row">
          {QUICK_TERMS.map((quickTerm) => (
            <button
              key={quickTerm}
              type="button"
              className="gb-chip"
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
      </div>

      {loadingPlan && (
        <div className="gb-plan-skeletons" aria-live="polite">
          <div className="gb-skeleton" style={{ height: 36 }} />
          <div className="gb-skeleton" style={{ height: 84 }} />
          <div className="gb-skeleton" style={{ height: 84 }} />
        </div>
      )}

      {planError && (
        <div className="gb-error">
          {typeof planError === "string" ? planError : JSON.stringify(planError)}
          <button type="button" className="gb-btn gb-btn-secondary" onClick={generatePlan}>
            Retry
          </button>
        </div>
      )}

      {plan && !loadingPlan && (
        <section className="gb-plan-timeline" aria-label="30-day timeline">
          <div className="gb-plan-summary">
            <div>
              <h4>{plan.plan_title}</h4>
              {plan.best_next_action && <p>{plan.best_next_action}</p>}
            </div>
            <div className="gb-plan-progress-pill">
              {completionSummary.done} / {completionSummary.total} tasks complete
            </div>
          </div>

          <div className="gb-plan-meta">
            Provider: {plan.llm_provider} | fallback: {String(plan.fallback_used)} | confidence: {plan.confidence}
          </div>

          {groupedTimeline.map(([week, items]) => (
            <div key={week} className="gb-week-block">
              <div className="gb-week-label">{week}</div>

              <div className="gb-week-tasks">
                {items.map(({ step, index, id }) => {
                  const isDone = Boolean(completed[id]);
                  const expanded = Boolean(expandedStepIds[id]);
                  const sourceIds = Array.isArray(step.source_node_ids) ? step.source_node_ids : [];

                  return (
                    <article key={id} className={`gb-plan-task ${isDone ? "gb-plan-task--done" : ""}`}>
                      <div className="gb-plan-task__row">
                        <button
                          type="button"
                          className={`gb-plan-task__check ${isDone ? "gb-plan-task__check--done" : ""}`}
                          onClick={() => toggleComplete(step, index)}
                          aria-label={isDone ? "Mark task incomplete" : "Mark task complete"}
                        >
                          {isDone ? "Done" : "Mark done"}
                        </button>

                        <div className="gb-plan-task__body">
                          <div className="gb-plan-task__topline">
                            <span className="gb-plan-task__range">{step.day_range || week}</span>
                            <button type="button" className="gb-link-btn" onClick={() => toggleExpand(step, index)}>
                              {expanded ? "Hide context" : "Why this matters culturally"}
                            </button>
                          </div>
                          <p>{step.action}</p>

                          {Array.isArray(step.entities) && step.entities.length > 0 && (
                            <div className="gb-plan-entities">
                              {step.entities.map((entity) => (
                                <span key={`${id}-${entity}`} className="gb-chip gb-chip--soft">
                                  {entity}
                                </span>
                              ))}
                            </div>
                          )}

                          {sourceIds.length > 0 && (
                            <div className="gb-plan-node-links">
                              <span>Connected graph nodes:</span>
                              {sourceIds.map((sourceId) => (
                                <button
                                  key={`${id}-${sourceId}`}
                                  type="button"
                                  className="gb-btn gb-btn-ghost"
                                  onClick={() => onFocusNode?.(sourceId)}
                                >
                                  {sourceId}
                                </button>
                              ))}
                            </div>
                          )}

                          {expanded && (
                            <div className="gb-plan-explain">
                              <strong>Why this matters culturally</strong>
                              <p>{step.dependency_reason}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            </div>
          ))}

          {(plan.warnings || []).length > 0 && (
            <div className="gb-plan-warnings">
              <strong>Heads up</strong>
              <ul>
                {plan.warnings.map((warning, index) => (
                  <li key={`${warning}-${index}`}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      <CulturalBridgeDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        bridge={bridge}
        loading={loadingBridge}
        error={bridgeError}
        onRetry={bridgeError ? retryBridge : undefined}
      />
    </div>
  );
}
