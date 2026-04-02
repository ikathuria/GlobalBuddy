import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { DataSet } from "vis-data";
import { Network } from "vis-network";

/** Single source for vis-network groups + legend swatches */
const GRAPH_GROUP_STYLES = {
  student: { bg: "#0c4a6e", border: "#38bdf8", label: "You" },
  mentor: { bg: "#0f766e", border: "#2dd4bf", label: "Mentor" },
  peer: { bg: "#4338ca", border: "#a5b4fc", label: "Peer" },
  restaurant: { bg: "#9a3412", border: "#fb923c", label: "Restaurant" },
  event: { bg: "#86198f", border: "#e879f9", label: "Event" },
  resource: { bg: "#075985", border: "#38bdf8", label: "Resource" },
  task: { bg: "#1e293b", border: "#94a3b8", label: "Task" },
};

const VIS_OPTIONS = {
  nodes: {
    font: { color: "#e2e8f0", size: 14, face: "Plus Jakarta Sans, system-ui, sans-serif" },
    borderWidth: 2,
    shadow: { enabled: true, color: "rgba(0,0,0,0.45)", size: 12 },
    margin: 14,
  },
  edges: {
    color: { color: "#64748b", opacity: 0.65 },
    smooth: { type: "continuous", roundness: 0.35 },
    width: 1.75,
  },
  physics: {
    stabilization: { iterations: 200, updateInterval: 25 },
    barnesHut: { gravitationalConstant: -3500, springLength: 200, springConstant: 0.04, damping: 0.5 },
  },
  interaction: {
    hover: true,
    tooltipDelay: 100,
    multiselect: false,
    navigationButtons: true,
    keyboard: { enabled: true, speed: { x: 8, y: 8, zoom: 0.02 } },
    zoomView: true,
    dragView: true,
  },
  layout: { improvedLayout: true },
  groups: Object.fromEntries(
    Object.entries(GRAPH_GROUP_STYLES).map(([k, v]) => [
      k,
      { color: { background: v.bg, border: v.border, highlight: { background: v.bg, border: "#f8fafc" } } },
    ]),
  ),
};

function edgeFrom(e) {
  return e.from ?? e.from_;
}

function GraphLegend() {
  return (
    <div className="gb-graph-legend" aria-label="Node colors by role">
      {Object.entries(GRAPH_GROUP_STYLES).map(([key, { bg, border, label }]) => (
        <span key={key} className="gb-graph-legend__item">
          <span className="gb-graph-legend__swatch" style={{ background: bg, borderColor: border }} />
          {label}
        </span>
      ))}
    </div>
  );
}

export default function GraphCanvas({ nodes, edges, onNodeSelect, selectedNodeId }) {
  const ref = useRef(null);
  const netRef = useRef(null);
  const roRef = useRef(null);
  const onNodeSelectRef = useRef(onNodeSelect);
  onNodeSelectRef.current = onNodeSelect;

  const [expanded, setExpanded] = useState(false);

  const hasGraph = Boolean(nodes?.length);

  const fitView = useCallback(() => {
    const net = netRef.current;
    if (!net) return;
    try {
      net.fit({ animation: { duration: 380, easingFunction: "easeInOutQuad" } });
    } catch {
      net.fit();
    }
  }, []);

  useEffect(() => {
    if (!expanded) return;
    const onKey = (e) => {
      if (e.key === "Escape") setExpanded(false);
    };
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [expanded]);

  useLayoutEffect(() => {
    if (!expanded || !netRef.current) return;
    const id = requestAnimationFrame(() => {
      netRef.current?.redraw();
      fitView();
    });
    return () => cancelAnimationFrame(id);
  }, [expanded, fitView]);

  useEffect(() => {
    if (!ref.current) return;
    if (!nodes?.length) {
      roRef.current?.disconnect();
      roRef.current = null;
      if (netRef.current) {
        netRef.current.destroy();
        netRef.current = null;
      }
      return;
    }

    const nds = new DataSet(
      nodes.map((n) => {
        const short = n.label.length > 30 ? `${n.label.slice(0, 28)}…` : n.label;
        const tip = [n.label, n.subtitle].filter(Boolean).join(" — ");
        return {
          id: n.id,
          label: short,
          group: n.group,
          title: tip,
          borderWidth: selectedNodeId === n.id ? 4 : 2,
        };
      }),
    );
    const eds = new DataSet(
      (edges || []).map((e) => ({
        id: e.id,
        from: edgeFrom(e),
        to: e.to,
      })),
    );

    if (netRef.current) {
      netRef.current.destroy();
      netRef.current = null;
    }
    roRef.current?.disconnect();

    const net = new Network(ref.current, { nodes: nds, edges: eds }, VIS_OPTIONS);
    net.on("click", (params) => {
      if (params.nodes.length) {
        const id = params.nodes[0];
        const full = nodes.find((nx) => nx.id === id);
        onNodeSelectRef.current?.(full ?? null);
      } else {
        onNodeSelectRef.current?.(null);
      }
    });
    net.on("stabilizationIterationsDone", () => {
      fitView();
    });

    netRef.current = net;

    const ro = new ResizeObserver(() => {
      if (netRef.current && ref.current) {
        netRef.current.redraw();
      }
    });
    ro.observe(ref.current);
    roRef.current = ro;

    return () => {
      ro.disconnect();
      roRef.current = null;
      net.destroy();
      netRef.current = null;
    };
  }, [nodes, edges, selectedNodeId, fitView]);

  const nCount = nodes?.length ?? 0;
  const eCount = edges?.length ?? 0;

  const innerHeight = expanded ? "min(78vh, 900px)" : "min(420px, 52vh)";

  const card = (
    <section className={`gb-card gb-graph-card ${expanded ? "gb-graph-card--expanded" : ""}`} aria-label="Evidence graph">
      <div className="gb-graph-card__top">
        <div className="gb-graph-card__intro">
          <h2 className="gb-graph-card__title">Evidence graph</h2>
          <p className="gb-graph-card__lede">
            This is the <strong>Neo4j evidence slice</strong> for your profile: people, places, and tasks returned by the graph.
            Lines show how you connect to each match; the gray chain is your recommended task order.
          </p>
          <ul className="gb-graph-card__tips">
            <li>
              <strong>Hover</strong> a node for its full name and subtitle.
            </li>
            <li>
              <strong>Click</strong> a node to open details below (great for judging walkthroughs).
            </li>
            <li>
              <strong>Scroll</strong> to zoom, <strong>drag</strong> the background to pan — or use the corner controls.
            </li>
          </ul>
          {hasGraph && (
            <p className="gb-graph-card__meta">
              <span className="gb-graph-card__stat">{nCount} nodes</span>
              <span className="gb-graph-card__stat">{eCount} links</span>
              <span className="gb-graph-card__hint">Grounded in live match results</span>
            </p>
          )}
        </div>
        {hasGraph && (
          <div className="gb-graph-card__actions">
            <button type="button" className="gb-btn gb-btn-secondary gb-graph-card__btn" onClick={fitView}>
              Fit view
            </button>
            <button
              type="button"
              className="gb-btn gb-btn-primary gb-graph-card__btn"
              onClick={() => setExpanded((x) => !x)}
            >
              {expanded ? "Exit full view" : "Expand for presentation"}
            </button>
          </div>
        )}
      </div>

      {hasGraph && <GraphLegend />}

      {!hasGraph ? (
        <div className="gb-graph-wrap gb-graph-placeholder">
          Run <strong>graph match</strong> on the left to load your evidence subgraph from Neo4j.
        </div>
      ) : (
        <div className={`gb-graph-stage ${expanded ? "gb-graph-stage--expanded" : ""}`}>
          <div ref={ref} className="gb-graph-canvas" style={{ height: innerHeight, width: "100%" }} />
        </div>
      )}
    </section>
  );

  if (!expanded) {
    return card;
  }

  return (
    <>
      <button
        type="button"
        className="gb-graph-backdrop"
        aria-label="Close expanded graph"
        onClick={() => setExpanded(false)}
      />
      <div className="gb-graph-expanded-shell">{card}</div>
    </>
  );
}
