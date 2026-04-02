import { useCallback, useMemo, useRef, useState } from "react";
import ProfileForm from "./components/ProfileForm.jsx";
import PlanPanel from "./components/PlanPanel.jsx";
import StatusPanel from "./components/StatusPanel.jsx";
import Banner from "./components/Banner.jsx";
import ExploreWorkspace from "./components/ExploreWorkspace.jsx";

const JOURNEY_STEPS = [
  { id: 1, title: "Profile", subtitle: "Tell us your context" },
  { id: 2, title: "AI Plan", subtitle: "Your first 30 days" },
  { id: 3, title: "Explore Graph", subtitle: "Find support nearby" },
];

export default function App() {
  const [match, setMatch] = useState(null);
  const [plan, setPlan] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [banner, setBanner] = useState(null);
  const [activeStep, setActiveStep] = useState(1);
  const [exploreCategory, setExploreCategory] = useState("people");
  const [pathPreview, setPathPreview] = useState([]);

  const stepRefs = {
    1: useRef(null),
    2: useRef(null),
    3: useRef(null),
  };

  const hasProfile = Boolean(match?.session_id);
  const hasPlan = Boolean(plan?.steps?.length);
  const returningToUs = hasProfile && match?.evidence_bundle?.student_profile?.new_to_us === false;

  const nodeIndex = useMemo(() => {
    return new Map((match?.subgraph?.nodes || []).map((node) => [node.id, node]));
  }, [match?.subgraph?.nodes]);

  const scrollToStep = useCallback(
    (step) => {
      const element = stepRefs[step]?.current;
      if (!element) return;
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    },
    [stepRefs],
  );

  const openStep = useCallback(
    (step) => {
      if (step > 1 && !hasProfile) {
        setActiveStep(1);
        setBanner({
          type: "error",
          message: "Start with your profile first. We will unlock your plan and graph right after.",
        });
        scrollToStep(1);
        return;
      }

      if (step === 2 && returningToUs) {
        setActiveStep(3);
        scrollToStep(3);
        return;
      }

      setActiveStep(step);
      scrollToStep(step);
    },
    [hasProfile, returningToUs, scrollToStep],
  );

  const onNodeSelect = useCallback((node) => {
    setSelectedNode(node);
  }, []);

  const handleProfileMatch = (data) => {
    const hasLivedInUsBefore = data?.evidence_bundle?.student_profile?.new_to_us === false;

    setMatch(data);
    setPlan(null);
    setSelectedNode(null);
    setPathPreview([]);
    setActiveStep(hasLivedInUsBefore ? 3 : 2);
    setExploreCategory("people");
    setBanner({
      type: "success",
      message: hasLivedInUsBefore
        ? "Profile saved. Since you have lived in the US before, we skipped the 30-day checklist and opened Explore Graph."
        : "Profile saved. Your personalized 30-day plan is ready to generate.",
    });

    requestAnimationFrame(() => {
      scrollToStep(hasLivedInUsBefore ? 3 : 2);
    });
  };

  const handleFocusNode = useCallback(
    (nodeId) => {
      const node = nodeIndex.get(nodeId);
      if (!node) return;
      setSelectedNode(node);
      setActiveStep(3);
      requestAnimationFrame(() => {
        scrollToStep(3);
      });
    },
    [nodeIndex, scrollToStep],
  );

  const heroPrimaryCta = () => {
    if (!hasProfile) {
      openStep(1);
      return;
    }
    openStep(returningToUs ? 3 : 2);
  };

  const heroSecondaryCta = () => {
    if (!hasProfile) {
      openStep(1);
      return;
    }
    openStep(3);
  };

  const stepState = (step) => {
    if (step === 1) return hasProfile ? "done" : activeStep === 1 ? "active" : "pending";
    if (step === 2) {
      if (!hasProfile) return "locked";
      if (returningToUs) return "done";
      if (hasPlan) return "done";
      return activeStep === 2 ? "active" : "pending";
    }
    if (!hasProfile) return "locked";
    return activeStep === 3 ? "active" : selectedNode ? "done" : "pending";
  };

  const stepHint = (step) => {
    if (step === 1 && hasProfile) return "Complete";
    if (step === 2 && returningToUs) return "Skipped";
    if (step === 2 && hasPlan) return "Plan ready";
    if (step === 3 && pathPreview.length > 1) return `Path: ${pathPreview.join(" -> ")}`;
    if (step > 1 && !hasProfile) return "Locked until profile is saved";
    return "In progress";
  };

  const isStepOpen = (step) => {
    if (!hasProfile && step > 1) return false;
    return activeStep === step;
  };

  const isStepLocked = (step) => step > 1 && !hasProfile;

  const profileName = match?.evidence_bundle?.student_profile?.full_name || "You";
  const heroSupportText = hasProfile
    ? returningToUs
      ? `Welcome back, ${profileName}. Since you already know US basics, jump straight into your local support graph.`
      : `Welcome back, ${profileName}. Continue with your AI plan and explore your support network when you are ready.`
    : "Start with a quick profile. We will map your first month, people, and local support so you do not have to guess alone.";

  const primaryLabel = hasProfile ? (returningToUs ? "Go to Explore Graph" : "Continue Your Plan") : "Start Your Plan";
  const secondaryLabel = hasProfile ? "Explore Nearby" : "Preview Explore Nearby";

  const stepSummary = (step) => {
    if (step === 1) {
      return "Share basic context so we can tailor support to your background and destination.";
    }
    if (step === 2) {
      return returningToUs
        ? "Skipped for returning US users so you can move straight to exploration."
        : "Get a calm, week-by-week action plan with culturally relevant context.";
    }
    return "Use your support graph to find mentors, housing leads, events, and practical next steps.";
  };

  const stepClass = (step) =>
    `gb-journey-step gb-journey-step--${stepState(step)} ${activeStep === step ? "gb-journey-step--current" : ""}`;

  const contentClass = (step) =>
    `gb-journey-content ${isStepOpen(step) ? "gb-journey-content--open" : "gb-journey-content--closed"}`;

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <div className="gb-brand">
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Global\u0926\u094B\u0938\u094D\u0924"}</span>
        </div>
        <div className="gb-nav-right">
          <StatusPanel compact />
        </div>
      </nav>

      <div className="gb-main">
        <header className="gb-hero gb-card">
          <p className="gb-hero-kicker">Your guided arrival journey</p>
          <h1>Find your footing in a new city with a plan that feels human, not overwhelming.</h1>
          <p>{heroSupportText}</p>
          <div className="gb-hero-ctas">
            <button type="button" className="gb-btn gb-btn-primary" onClick={heroPrimaryCta}>
              {primaryLabel}
            </button>
            <button type="button" className="gb-btn gb-btn-secondary" onClick={heroSecondaryCta}>
              {secondaryLabel}
            </button>
          </div>
        </header>

        {banner?.message && <Banner type={banner.type} message={banner.message} onDismiss={() => setBanner(null)} />}

        <section className="gb-journey-shell" aria-label="Guided onboarding steps">
          <ol className="gb-journey-track" aria-label="Onboarding progress">
            {JOURNEY_STEPS.map((step) => (
              <li key={step.id} className={`gb-journey-dot gb-journey-dot--${stepState(step.id)}`}>
                <button type="button" onClick={() => openStep(step.id)} disabled={isStepLocked(step.id)}>
                  <span>{step.title}</span>
                  <small>{stepHint(step.id)}</small>
                </button>
              </li>
            ))}
          </ol>

          <article ref={stepRefs[1]} className="gb-card gb-journey-card" id="step-profile">
            <div className="gb-journey-head">
              <button type="button" className={stepClass(1)} onClick={() => openStep(1)} aria-expanded={isStepOpen(1)}>
                <span className="gb-journey-step__index">Step 1</span>
                <span className="gb-journey-step__title">Profile</span>
                <span className="gb-journey-step__subtitle">Tell us your context</span>
                <span className="gb-journey-step__state">{stepState(1) === "done" ? "Done" : "Open"}</span>
              </button>
              <p className="gb-journey-copy">{stepSummary(1)}</p>
            </div>
            <div className={contentClass(1)}>
              <ProfileForm onMatch={handleProfileMatch} />
            </div>
          </article>

          <article ref={stepRefs[2]} className="gb-card gb-journey-card" id="step-plan">
            <div className="gb-journey-head">
              <button
                type="button"
                className={stepClass(2)}
                onClick={() => openStep(2)}
                disabled={isStepLocked(2)}
                aria-expanded={isStepOpen(2)}
              >
                <span className="gb-journey-step__index">Step 2</span>
                <span className="gb-journey-step__title">AI Plan</span>
                <span className="gb-journey-step__subtitle">Your first 30 days</span>
                <span className="gb-journey-step__state">
                  {stepState(2) === "done" ? "Done" : stepState(2) === "locked" ? "Locked" : "Open"}
                </span>
              </button>
              <p className="gb-journey-copy">{stepSummary(2)}</p>
            </div>
            <div className={contentClass(2)}>
              {hasProfile ? (
                returningToUs ? (
                  <div className="gb-journey-lock">
                    30-day checklist skipped because you selected that you have already lived in the US.
                    <div style={{ marginTop: "0.55rem" }}>
                      <button type="button" className="gb-btn gb-btn-primary" onClick={() => openStep(3)}>
                        Continue to Explore Graph
                      </button>
                    </div>
                  </div>
                ) : (
                  <PlanPanel
                    sessionId={match?.session_id}
                    matchPayload={match}
                    onPlanReady={setPlan}
                    onFocusNode={handleFocusNode}
                    onOpenExplore={() => openStep(3)}
                  />
                )
              ) : (
                <div className="gb-journey-lock">Complete Step 1 first to unlock your AI onboarding plan.</div>
              )}
            </div>
          </article>

          <article ref={stepRefs[3]} className="gb-card gb-journey-card" id="step-graph">
            <div className="gb-journey-head">
              <button
                type="button"
                className={stepClass(3)}
                onClick={() => openStep(3)}
                disabled={isStepLocked(3)}
                aria-expanded={isStepOpen(3)}
              >
                <span className="gb-journey-step__index">Step 3</span>
                <span className="gb-journey-step__title">Explore Graph</span>
                <span className="gb-journey-step__subtitle">Find support nearby</span>
                <span className="gb-journey-step__state">
                  {stepState(3) === "done" ? "Done" : stepState(3) === "locked" ? "Locked" : "Open"}
                </span>
              </button>
              <p className="gb-journey-copy">{stepSummary(3)}</p>
            </div>
            <div className={contentClass(3)}>
              {hasProfile ? (
                <ExploreWorkspace
                  match={match}
                  plan={plan}
                  category={exploreCategory}
                  onCategoryChange={setExploreCategory}
                  selectedNode={selectedNode}
                  onNodeSelect={onNodeSelect}
                  onClearNode={() => setSelectedNode(null)}
                  onPathChange={setPathPreview}
                />
              ) : (
                <div className="gb-journey-lock">Complete Step 1 first to unlock your support graph.</div>
              )}
            </div>
          </article>
        </section>

        {match?.session_id && (
          <footer className="gb-footer">
            Session <code>{match.session_id}</code>
          </footer>
        )}
      </div>
    </div>
  );
}
