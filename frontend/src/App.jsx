import { useCallback, useState } from "react";
import ProfileForm from "./components/ProfileForm.jsx";
import GraphCanvas from "./components/GraphCanvas.jsx";
import PlanPanel from "./components/PlanPanel.jsx";
import StatusPanel from "./components/StatusPanel.jsx";
import MatchCards from "./components/MatchCards.jsx";
import Banner from "./components/Banner.jsx";
import NodeDetailCard from "./components/NodeDetailCard.jsx";
import CommunitySignup from "./components/CommunitySignup.jsx";
import CommunityFitPanel from "./components/CommunityFitPanel.jsx";

export default function App() {
  const [match, setMatch] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [banner, setBanner] = useState(null);

  const onNodeSelect = useCallback((node) => {
    setSelectedNode(node);
  }, []);

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <div className="gb-brand">
          <span className="gb-mark" aria-hidden="true" />
          <span>GlobalBuddy</span>
        </div>
        <span className="gb-nav-tag">Neo4j · AI</span>
      </nav>

      <div className="gb-main">
        <header className="gb-hero">
          <h1>Your command center for settling in.</h1>
          <p>
            Neo4j-backed matches, an evidence graph you can explore, and structured AI for plans and cultural bridge terms
            — grounded in what the graph actually contains.
          </p>
        </header>

        <StatusPanel />

        {banner?.message && (
          <Banner type={banner.type} message={banner.message} onDismiss={() => setBanner(null)} />
        )}

        <div className="gb-command">
          <div className="gb-col gb-col-left">
            <CommunitySignup />
            <ProfileForm
              onMatch={(data) => {
                setMatch(data);
                setSelectedNode(null);
                setBanner({ type: "success", message: "Graph match ready — review mentors, explore the evidence graph, then generate your plan." });
              }}
            />
          </div>

          <div className="gb-col gb-col-center">
            <MatchCards match={match} />
            <CommunityFitPanel match={match} />
            <GraphCanvas
              nodes={match?.subgraph?.nodes}
              edges={match?.subgraph?.edges}
              onNodeSelect={onNodeSelect}
              selectedNodeId={selectedNode?.id}
            />
            <NodeDetailCard node={selectedNode} onClear={() => setSelectedNode(null)} />
          </div>

          <div className="gb-col gb-col-right">
            <PlanPanel sessionId={match?.session_id} matchPayload={match} />
          </div>
        </div>

        {match?.session_id && (
          <footer className="gb-footer">
            Session <code>{match.session_id}</code>
          </footer>
        )}
      </div>
    </div>
  );
}
