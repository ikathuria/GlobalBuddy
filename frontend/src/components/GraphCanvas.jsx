import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { DataSet } from "vis-data";
import { Network } from "vis-network";

const GRAPH_GROUP_STYLES = {
  student: { bg: "#0f766e", border: "#14b8a6", label: "You" },
  mentor: { bg: "#0369a1", border: "#38bdf8", label: "Mentor" },
  peer: { bg: "#1d4ed8", border: "#60a5fa", label: "Peer" },
  restaurant: { bg: "#0e7490", border: "#67e8f9", label: "Food" },
  event: { bg: "#0f766e", border: "#5eead4", label: "Event" },
  resource: { bg: "#0f172a", border: "#94a3b8", label: "Resource" },
  task: { bg: "#334155", border: "#cbd5e1", label: "Task" },
  place_worship: { bg: "#155e75", border: "#67e8f9", label: "Worship" },
  grocery: { bg: "#166534", border: "#4ade80", label: "Grocery" },
  housing_area: { bg: "#1e3a8a", border: "#93c5fd", label: "Housing" },
  exploration: { bg: "#0f766e", border: "#5eead4", label: "Explore" },
  transit_tip: { bg: "#1e293b", border: "#94a3b8", label: "Transit" },
};

const FILTER_GROUPS = [
  { id: "people", label: "People", groups: ["student", "mentor", "peer"] },
  { id: "events", label: "Events", groups: ["event"] },
  { id: "places", label: "Places", groups: ["housing_area", "grocery", "restaurant", "place_worship", "exploration"] },
  { id: "support", label: "Support", groups: ["resource", "task", "transit_tip"] },
];

const VIS_OPTIONS = {
  nodes: {
    font: { color: "#e2e8f0", size: 14, face: "Sora, system-ui, sans-serif" },
    borderWidth: 2,
    shadow: { enabled: true, color: "rgba(0,0,0,0.2)", size: 10 },
    margin: 14,
    shape: "dot",
    size: 14,
  },
  edges: {
    color: { color: "#7c8fa6", opacity: 0.65 },
    smooth: { type: "continuous", roundness: 0.26 },
    width: 1.8,
  },
  physics: {
    stabilization: { iterations: 180, updateInterval: 20 },
    barnesHut: { gravitationalConstant: -2900, springLength: 170, springConstant: 0.045, damping: 0.52 },
  },
  interaction: {
    hover: true,
    tooltipDelay: 120,
    multiselect: false,
    navigationButtons: false,
    keyboard: { enabled: true, speed: { x: 8, y: 8, zoom: 0.03 } },
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

function buildAdjacency(nodes, edges) {
  const adjacency = new Map();
  nodes.forEach((node) => {
    adjacency.set(node.id, []);
  });

  edges.forEach((edge) => {
    const from = edgeFrom(edge);
    const to = edge.to;
    if (!adjacency.has(from) || !adjacency.has(to)) return;
    adjacency.get(from).push(to);
    adjacency.get(to).push(from);
  });

  return adjacency;
}

function shortestPath(nodes, edges, startId, endId) {
  if (!startId || !endId || startId === endId) return startId && endId ? [startId] : [];

  const adjacency = buildAdjacency(nodes, edges);
  if (!adjacency.has(startId) || !adjacency.has(endId)) return [];

  const queue = [startId];
  const parent = new Map([[startId, null]]);

  while (queue.length) {
    const current = queue.shift();
    if (current === endId) break;

    const neighbors = adjacency.get(current) || [];
    neighbors.forEach((neighbor) => {
      if (parent.has(neighbor)) return;
      parent.set(neighbor, current);
      queue.push(neighbor);
    });
  }

  if (!parent.has(endId)) return [];

  const path = [];
  let pointer = endId;
  while (pointer != null) {
    path.push(pointer);
    pointer = parent.get(pointer) ?? null;
  }

  return path.reverse();
}

function PathLegend() {
  return (
    <div className="gb-graph-legend" aria-label="Node colors by role">
      {Object.entries(GRAPH_GROUP_STYLES).map(([key, style]) => (
        <span key={key} className="gb-graph-legend__item">
          <span className="gb-graph-legend__swatch" style={{ background: style.bg, borderColor: style.border }} />
          {style.label}
        </span>
      ))}
    </div>
  );
}

export default function GraphCanvas({
  nodes,
  edges,
  onNodeSelect,
  selectedNodeId,
  compact = false,
  onPathComputed,
}) {
  const ref = useRef(null);
  const netRef = useRef(null);
  const roRef = useRef(null);
  const onNodeSelectRef = useRef(onNodeSelect);
  const onPathComputedRef = useRef(onPathComputed);

  onNodeSelectRef.current = onNodeSelect;
  onPathComputedRef.current = onPathComputed;

  const [expanded, setExpanded] = useState(false);
  const [activeFilterIds, setActiveFilterIds] = useState(() => new Set(FILTER_GROUPS.map((group) => group.id)));

  const hasGraph = Boolean(nodes?.length);

  const shouldShowGroup = useCallback(
    (groupName) => {
      if (!groupName) return true;
      if (!activeFilterIds.size) return true;
      return FILTER_GROUPS.some((filter) => activeFilterIds.has(filter.id) && filter.groups.includes(groupName));
    },
    [activeFilterIds],
  );

  const filteredNodes = useMemo(() => {
    return (nodes || []).filter((node) => shouldShowGroup(node.group));
  }, [nodes, shouldShowGroup]);

  const visibleIds = useMemo(() => new Set(filteredNodes.map((node) => node.id)), [filteredNodes]);

  const filteredEdges = useMemo(() => {
    return (edges || []).filter((edge) => {
      const from = edgeFrom(edge);
      return visibleIds.has(from) && visibleIds.has(edge.to);
    });
  }, [edges, visibleIds]);

  const studentNodeId = useMemo(() => {
    const student = filteredNodes.find((node) => node.group === "student") || filteredNodes[0];
    return student?.id;
  }, [filteredNodes]);

  const currentPath = useMemo(() => {
    if (!selectedNodeId) return [];
    return shortestPath(filteredNodes, filteredEdges, studentNodeId, selectedNodeId);
  }, [filteredNodes, filteredEdges, selectedNodeId, studentNodeId]);

  const pathLabels = useMemo(() => {
    if (!currentPath.length) return [];
    const labelsById = new Map((filteredNodes || []).map((node) => [node.id, node.label]));
    return currentPath.map((id) => labelsById.get(id) || id);
  }, [filteredNodes, currentPath]);

  useEffect(() => {
    if (!onPathComputedRef.current) return;
    onPathComputedRef.current(pathLabels);
  }, [pathLabels]);

  const fitView = useCallback(() => {
    const network = netRef.current;
    if (!network) return;
    try {
      network.fit({ animation: { duration: 320, easingFunction: "easeInOutQuad" } });
    } catch {
      network.fit();
    }
  }, []);

  useLayoutEffect(() => {
    if (!expanded || !netRef.current) return;

    const handle = requestAnimationFrame(() => {
      netRef.current?.redraw();
      fitView();
    });

    return () => cancelAnimationFrame(handle);
  }, [expanded, fitView]);

  useEffect(() => {
    if (!ref.current) return;

    if (!filteredNodes.length) {
      roRef.current?.disconnect();
      roRef.current = null;
      if (netRef.current) {
        netRef.current.destroy();
        netRef.current = null;
      }
      return;
    }

    const pathNodeSet = new Set(currentPath);
    const pathEdgeSet = new Set();
    for (let index = 0; index < currentPath.length - 1; index += 1) {
      const from = currentPath[index];
      const to = currentPath[index + 1];
      pathEdgeSet.add(`${from}::${to}`);
      pathEdgeSet.add(`${to}::${from}`);
    }

    const datasetNodes = new DataSet(
      filteredNodes.map((node) => {
        const shortLabel = node.label.length > 30 ? `${node.label.slice(0, 28)}...` : node.label;
        const tip = [node.label, node.subtitle].filter(Boolean).join(" | ");

        const isSelected = selectedNodeId === node.id;
        const onPath = pathNodeSet.has(node.id);

        return {
          id: node.id,
          label: shortLabel,
          group: node.group,
          title: tip,
          borderWidth: isSelected ? 5 : onPath ? 4 : 2,
          size: isSelected ? 18 : onPath ? 16 : 14,
          shadow: onPath
            ? { enabled: true, color: "rgba(20,184,166,0.45)", size: 20 }
            : { enabled: true, color: "rgba(0,0,0,0.25)", size: 10 },
        };
      }),
    );

    const datasetEdges = new DataSet(
      filteredEdges.map((edge, index) => {
        const from = edgeFrom(edge);
        const key = `${from}::${edge.to}`;
        const highlighted = pathEdgeSet.has(key);
        return {
          id: edge.id || `${from}-${edge.to}-${index}`,
          from,
          to: edge.to,
          width: highlighted ? 4 : 1.8,
          color: highlighted ? "#14b8a6" : "#7c8fa6",
          dashes: highlighted ? false : [5, 4],
        };
      }),
    );

    if (netRef.current) {
      netRef.current.destroy();
      netRef.current = null;
    }
    roRef.current?.disconnect();

    const network = new Network(ref.current, { nodes: datasetNodes, edges: datasetEdges }, VIS_OPTIONS);

    network.on("click", (params) => {
      if (params.nodes.length) {
        const id = params.nodes[0];
        const full = filteredNodes.find((node) => node.id === id) || null;
        onNodeSelectRef.current?.(full);
        return;
      }
      onNodeSelectRef.current?.(null);
    });

    network.on("stabilizationIterationsDone", () => {
      fitView();
    });

    netRef.current = network;

    const observer = new ResizeObserver(() => {
      if (!netRef.current || !ref.current) return;
      netRef.current.redraw();
    });
    observer.observe(ref.current);
    roRef.current = observer;

    return () => {
      observer.disconnect();
      roRef.current = null;
      network.destroy();
      netRef.current = null;
    };
  }, [filteredNodes, filteredEdges, selectedNodeId, currentPath, fitView]);

  const nodeCount = filteredNodes.length;
  const edgeCount = filteredEdges.length;
  const innerHeight = expanded ? "min(78vh, 900px)" : compact ? "min(320px, 42vh)" : "min(420px, 52vh)";

  const toggleFilter = (id) => {
    setActiveFilterIds((previous) => {
      const next = new Set(previous);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const clearFilters = () => {
    setActiveFilterIds(new Set(FILTER_GROUPS.map((group) => group.id)));
  };

  const showDetailed = !compact || expanded;

  return (
    <section className={`gb-graph-card ${expanded ? "gb-graph-card--expanded" : ""}`} aria-label="Support graph">
      <div className="gb-graph-card__top">
        <div className="gb-graph-card__intro">
          <h4>Support graph</h4>
          <p>
            Explore relationships across people, places, and support resources. Select a node to reveal details and next actions.
          </p>
          {pathLabels.length > 1 && (
            <div className="gb-graph-path">
              Shortest path: {pathLabels.join(" -> ")}
            </div>
          )}
          <div className="gb-graph-meta">
            <span>{nodeCount} nodes</span>
            <span>{edgeCount} links</span>
          </div>
        </div>

        <div className="gb-graph-card__actions">
          <button type="button" className="gb-btn gb-btn-ghost" onClick={fitView}>
            Fit view
          </button>
          <button type="button" className="gb-btn gb-btn-secondary" onClick={clearFilters}>
            Reset filters
          </button>
          <button type="button" className="gb-btn gb-btn-primary" onClick={() => setExpanded((value) => !value)}>
            {expanded ? "Collapse graph" : "Expand graph"}
          </button>
        </div>
      </div>

      <div className="gb-graph-filters" role="group" aria-label="Graph filters">
        {FILTER_GROUPS.map((filter) => {
          const selected = activeFilterIds.has(filter.id);
          return (
            <button
              key={filter.id}
              type="button"
              className={`gb-pill-tab ${selected ? "gb-pill-tab--active" : ""}`}
              onClick={() => toggleFilter(filter.id)}
              aria-pressed={selected}
            >
              {filter.label}
            </button>
          );
        })}
      </div>

      {showDetailed && <PathLegend />}

      {!hasGraph ? (
        <div className="gb-graph-placeholder">
          Save your profile in Step 1 to load your graph-backed support network.
        </div>
      ) : !filteredNodes.length ? (
        <div className="gb-graph-placeholder">No nodes visible. Re-enable one or more filters.</div>
      ) : (
        <div className={`gb-graph-stage ${expanded ? "gb-graph-stage--expanded" : ""}`}>
          <div ref={ref} className="gb-graph-canvas" style={{ height: innerHeight, width: "100%" }} />
        </div>
      )}
    </section>
  );
}
