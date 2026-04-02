import { useCallback, useState } from "react";
import ProfileForm from "./components/ProfileForm.jsx";
import PlanPanel from "./components/PlanPanel.jsx";
import StatusPanel from "./components/StatusPanel.jsx";
import Banner from "./components/Banner.jsx";
import ExploreWorkspace from "./components/ExploreWorkspace.jsx";

export default function App() {
  const [match, setMatch] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [banner, setBanner] = useState(null);
  const [mode, setMode] = useState("survival");
  const [exploreCategory, setExploreCategory] = useState("people");

  const onNodeSelect = useCallback((node) => {
    setSelectedNode(node);
  }, []);

  const hasProfile = Boolean(match?.session_id);
  const newToUs = Boolean(match?.evidence_bundle?.student_profile?.new_to_us);
  const flowHint =
    mode === "survival"
      ? newToUs
        ? "New to the US is turned on, so this opens in Survival mode first. Flip to Explore whenever you are ready."
        : "Use Survival mode for first 30-day priorities and quick US-term explanations."
      : "Use Explore mode for people, places, and resources. Switch back to Survival anytime.";

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setSelectedNode(null);
  };

  const handleProfileMatch = (data) => {
    setMatch(data);
    setSelectedNode(null);
    const shouldStartInSurvival = Boolean(data?.evidence_bundle?.student_profile?.new_to_us);
    setMode(shouldStartInSurvival ? "survival" : "explore");
    setExploreCategory("people");
    setBanner({
      type: "success",
      message: shouldStartInSurvival
        ? "Profile saved. Starting in Survival Plan mode for your US arrival."
        : "Profile saved. Starting in Explore mode for nearby connections and resources.",
    });
  };

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <div className="gb-brand">
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Global\u0926\u094B\u0938\u094D\u0924"}</span>
        </div>
        <div className="gb-nav-right">
          <StatusPanel compact />
          <span className="gb-nav-tag">Neo4j | AI</span>
        </div>
      </nav>

      <div className="gb-main">
        <header className="gb-hero">
          <h1>You didn't come this far to figure it out alone.</h1>
          <p>
            Start with your profile, get arrival guidance if you are new to the US, then flip into Explore mode to find
            people, events, places, and resources nearby.
          </p>
        </header>

        {banner?.message && (
          <Banner type={banner.type} message={banner.message} onDismiss={() => setBanner(null)} />
        )}

        {!hasProfile ? (
          <section className="gb-onboarding-wrap" aria-label="Profile onboarding">
            <div className="gb-card gb-onboarding-card">
              <h2 className="gb-card-title--plain">{"Welcome to Global\u0926\u094B\u0938\u094D\u0924"}</h2>
              <p className="gb-onboarding-copy">
                Step 1 of 3 starts here. Fill your profile once and we will personalize everything after it.
              </p>
            </div>
            <ProfileForm onMatch={handleProfileMatch} />
          </section>
        ) : (
          <div className="gb-command">
            <section className="gb-card gb-flow-shell">
              <div className="gb-flow-shell__row">
                <h2 className="gb-card-title--plain">Your flow</h2>
                <div className="gb-flow-switch" role="tablist" aria-label="Choose user flow mode">
                  <button
                    type="button"
                    role="tab"
                    aria-selected={mode === "survival"}
                    className={`gb-flow-btn ${mode === "survival" ? "gb-flow-btn--active" : ""}`}
                    onClick={() => switchMode("survival")}
                  >
                    Survival + Cultural Bridge
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={mode === "explore"}
                    className={`gb-flow-btn ${mode === "explore" ? "gb-flow-btn--active" : ""}`}
                    onClick={() => switchMode("explore")}
                  >
                    Explore Nearby
                  </button>
                </div>
              </div>
              <p className="gb-flow-hint">{flowHint}</p>
            </section>

            <div className="gb-command-body">
              <div className="gb-col gb-col-left">
                <ProfileForm onMatch={handleProfileMatch} />
              </div>
              <div className="gb-col gb-col-main">
                {mode === "survival" ? (
                  <PlanPanel sessionId={match?.session_id} matchPayload={match} />
                ) : (
                  <ExploreWorkspace
                    match={match}
                    category={exploreCategory}
                    onCategoryChange={setExploreCategory}
                    selectedNode={selectedNode}
                    onNodeSelect={onNodeSelect}
                    onClearNode={() => setSelectedNode(null)}
                  />
                )}
              </div>
            </div>
          </div>
        )}

        {match?.session_id && (
          <footer className="gb-footer">
            Session <code>{match.session_id}</code>
          </footer>
        )}
      </div>
    </div>
  );
}
