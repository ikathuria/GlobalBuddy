import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { DataSet } from "vis-data";
import { Network } from "vis-network";

const GRAPH_GROUP_STYLES = {
  student: { bg: "#0c4a6e", border: "#38bdf8", label: "You" },
  mentor: { bg: "#0f766e", border: "#2dd4bf", label: "Mentor" },
  peer: { bg: "#4338ca", border: "#a5b4fc", label: "Peer" },
  restaurant: { bg: "#9a3412", border: "#fb923c", label: "Restaurant" },
  event: { bg: "#86198f", border: "#e879f9", label: "Event" },
  resource: { bg: "#075985", border: "#38bdf8", label: "Resource" },
  task: { bg: "#1e293b", border: "#94a3b8", label: "Task" },
  place_worship: { bg: "#4c1d95", border: "#c4b5fd", label: "Worship" },
  grocery: { bg: "#14532d", border: "#86efac", label: "Grocery" },
  housing_area: { bg: "#713f12", border: "#fcd34d", label: "Housing" },
  exploration: { bg: "#0e7490", border: "#67e8f9", label: "Explore" },
  transit_tip: { bg: "#334155", border: "#cbd5e1", label: "Transit" },
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
    Object.entries(GRAPH_GROUP_STYLES).map(([key, value]) => [
      key,
      { color: { background: value.bg, border: value.border, highlight: { background: value.bg, border: "#f8fafc" } } },
    ]),
  ),
};

function edgeFrom(edge) {
  return edge.from ?? edge.from_;
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

export default function GraphCanvas({ nodes, edges, onNodeSelect, selectedNodeId, compact = false }) {
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
    const onKey = (event) => {
      if (event.key === "Escape") setExpanded(false);
    };
    window.addEventListener("keydown", onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = previousOverflow;
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
      nodes.map((node) => {
        const short = node.label.length > 30 ? `${node.label.slice(0, 28)}...` : node.label;
        const tip = [node.label, node.subtitle].filter(Boolean).join(" - ");
        return {
          id: node.id,
          label: short,
          group: node.group,
          title: tip,
          borderWidth: selectedNodeId === node.id ? 4 : 2,
        };
      }),
    );

    const eds = new DataSet(
      (edges || []).map((edge) => ({
        id: edge.id,
        from: edgeFrom(edge),
        to: edge.to,
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
        const full = nodes.find((candidate) => candidate.id === id);
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

  const nodeCount = nodes?.length ?? 0;
  const edgeCount = edges?.length ?? 0;
  const innerHeight = expanded ? "min(78vh, 900px)" : compact ? "min(320px, 44vh)" : "min(420px, 52vh)";

  const showDetailed = !compact || expanded;
  const title = compact ? "Explore graph" : "Evidence graph";
  const lede = showDetailed
    ? "This is the Neo4j evidence slice for your profile: people, places, and tasks returned by the graph."
    : "Graph view of people, places, and tasks for the selected category.";

  const card = (
    <section className={`gb-card gb-graph-card ${expanded ? "gb-graph-card--expanded" : ""}`} aria-label="Evidence graph">
      <div className="gb-graph-card__top">
        <div className="gb-graph-card__intro">
          <h2 className="gb-graph-card__title">{title}</h2>
          <p className="gb-graph-card__lede">{lede}</p>

          {showDetailed && (
            <ul className="gb-graph-card__tips">
              <li>
                <strong>Hover</strong> a node for its full name and subtitle.
              </li>
              <li>
                <strong>Click</strong> a node to open details below.
              </li>
              <li>
                <strong>Scroll</strong> to zoom and <strong>drag</strong> to pan.
              </li>
            </ul>
          )}

          {hasGraph && (
            <p className="gb-graph-card__meta">
              <span className="gb-graph-card__stat">{nodeCount} nodes</span>
              <span className="gb-graph-card__stat">{edgeCount} links</span>
              {showDetailed && <span className="gb-graph-card__hint">Grounded in live match results</span>}
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
              onClick={() => setExpanded((value) => !value)}
            >
              {expanded ? "Exit full screen" : compact ? "Full screen graph" : "Expand for presentation"}
            </button>
          </div>
        )}
      </div>

      {hasGraph && showDetailed && <GraphLegend />}

      {!hasGraph ? (
        <div className="gb-graph-wrap gb-graph-placeholder">
          Run <strong>graph match</strong> in profile setup to load your evidence subgraph from Neo4j.
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
      <div
        className="gb-graph-backdrop"
        role="presentation"
        onMouseDown={(event) => {
          if (event.target === event.currentTarget) {
            setExpanded(false);
          }
        }}
      />
      <div className="gb-graph-expanded-shell" onMouseDown={(event) => event.stopPropagation()}>
        {card}
      </div>
    </>
  );
}
