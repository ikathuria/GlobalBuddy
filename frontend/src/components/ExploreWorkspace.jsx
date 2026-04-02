import { useMemo, useState } from "react";
import GraphCanvas from "./GraphCanvas.jsx";
import NodeDetailCard from "./NodeDetailCard.jsx";

const CATEGORY_OPTIONS = [
  { id: "people", label: "People" },
  { id: "events", label: "Events" },
  { id: "food", label: "Food" },
  { id: "housing", label: "Housing" },
  { id: "tasks", label: "Tasks" },
];

function mapsHref(item) {
  const direct = (item?.maps_link || "").trim();
  if (direct) return direct;
  const query = (item?.maps_query || item?.address || item?.location || item?.name || "").trim();
  if (!query) return "";
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

function toPct(value) {
  if (value == null || Number.isNaN(Number(value))) return null;
  return `${Math.round(Number(value) * 100)}%`;
}

function initials(name) {
  const words = String(name || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (!words.length) return "?";
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return `${words[0][0]}${words[1][0]}`.toUpperCase();
}

function avatarTone(seed) {
  const value = Array.from(seed || "x").reduce((sum, char) => sum + char.charCodeAt(0), 0);
  const tones = ["teal", "sky", "mint", "blue", "aqua"];
  return tones[value % tones.length];
}

function first(items, count) {
  return (Array.isArray(items) ? items : []).slice(0, count);
}

function buildCategoryData(match, plan) {
  const mentors = first(match?.mentors_top3, 6).map((mentor) => ({
    cardId: `mentor-${mentor.id}`,
    id: mentor.id,
    title: mentor.name,
    kind: "Mentor",
    nodeId: mentor.id,
    subtitle: mentor.match_reasons?.join(" | ") || "Mentor from your graph",
    description: mentor.connect_hint || "Great first contact for practical local advice.",
    why: mentor.why_this_match || "Shared background and need overlap made this a strong match.",
    avatar: initials(mentor.name),
    avatarTone: avatarTone(mentor.id),
    trustSignals: [
      toPct(mentor.confidence_score ?? mentor.match_score) ? `Match ${toPct(mentor.confidence_score ?? mentor.match_score)}` : null,
      mentor.trust_score != null ? `Trust ${Number(mentor.trust_score).toFixed(2)}` : null,
    ].filter(Boolean),
    detailLines: [
      mentor.why_this_match ? `Cultural fit: ${mentor.why_this_match}` : null,
      mentor.connect_hint ? `How to reach out: ${mentor.connect_hint}` : null,
    ].filter(Boolean),
    cta: mentor.email ? { label: "Email", href: `mailto:${encodeURIComponent(mentor.email)}` } : null,
  }));

  const peers = first(match?.peers_nearby, 6).map((peer) => ({
    cardId: `peer-${peer.id}`,
    id: peer.id,
    title: peer.name,
    kind: "Peer",
    nodeId: peer.id,
    subtitle: [peer.university, peer.neighborhood].filter(Boolean).join(" | ") || "Peer nearby",
    description: peer.connect_hint || "A student connection for social and campus navigation.",
    why: "Shared destination context can reduce first-week overwhelm.",
    avatar: initials(peer.name),
    avatarTone: avatarTone(peer.id),
    trustSignals: [peer.neighborhood ? `Nearby: ${peer.neighborhood}` : null].filter(Boolean),
    detailLines: [
      peer.connect_hint ? `How to connect: ${peer.connect_hint}` : null,
      peer.university ? `University context: ${peer.university}` : null,
    ].filter(Boolean),
    cta: peer.email ? { label: "Email", href: `mailto:${encodeURIComponent(peer.email)}` } : null,
  }));

  const events = first(match?.community_events, 8).map((event) => ({
    cardId: `event-${event.id}`,
    id: event.id,
    title: event.name,
    kind: "Event",
    nodeId: event.id,
    subtitle: [event.category, event.start_time].filter(Boolean).join(" | "),
    description: event.notes || "Community touchpoint to build belonging in your first month.",
    why: "Joining one event early can unlock your support network faster.",
    avatar: "EV",
    avatarTone: "blue",
    trustSignals: [event.location ? `Location: ${event.location}` : null].filter(Boolean),
    detailLines: [event.notes || null].filter(Boolean),
    cta: mapsHref(event) ? { label: "Open maps", href: mapsHref(event) } : null,
  }));

  const food = [
    ...first(match?.grocery_stores, 4).map((item) => ({
      cardId: `grocery-${item.id}`,
      id: item.id,
      title: item.name,
      kind: "Grocery",
      nodeId: item.id,
      subtitle: [item.neighborhood, item.address].filter(Boolean).join(" | "),
      description: item.why_recommended || "Reliable essentials near your destination.",
      why: "Food familiarity can reduce transition stress quickly.",
      avatar: "FO",
      avatarTone: "mint",
      trustSignals: [item.subtype || null].filter(Boolean),
      detailLines: [item.why_recommended || null].filter(Boolean),
      cta: mapsHref(item) ? { label: "Open maps", href: mapsHref(item) } : null,
    })),
    ...first(match?.cultural_restaurants, 4).map((item) => ({
      cardId: `restaurant-${item.id}`,
      id: item.id,
      title: item.name,
      kind: "Food",
      nodeId: item.id,
      subtitle: item.distance_km != null ? `${item.distance_km} km` : "Restaurant",
      description: "Comfort food option connected to your profile context.",
      why: "Small comfort routines make difficult weeks easier.",
      avatar: "FD",
      avatarTone: "teal",
      trustSignals: [item.price_level != null ? `Price level ${item.price_level}` : null].filter(Boolean),
      detailLines: ["Comfort-food node from your graph evidence."],
      cta: null,
    })),
  ];

  const housing = [
    ...first(match?.housing_areas, 8).map((item) => ({
      cardId: `housing-${item.id}`,
      id: item.id,
      title: item.name,
      kind: "Housing",
      nodeId: item.id,
      subtitle: [item.neighborhood, item.address].filter(Boolean).join(" | "),
      description: item.why_recommended || "Area connected to your goals and commute needs.",
      why: "Choosing a stable base early improves everything else in your plan.",
      avatar: "HS",
      avatarTone: "sky",
      trustSignals: [item.subtype || null].filter(Boolean),
      detailLines: [item.why_recommended || null].filter(Boolean),
      cta: mapsHref(item) ? { label: "Open maps", href: mapsHref(item) } : null,
    })),
    ...first(match?.resources, 4).map((resource) => ({
      cardId: `resource-${resource.id}`,
      id: resource.id,
      title: resource.name,
      kind: "Resource",
      nodeId: resource.id,
      subtitle: resource.resource_type || "Support resource",
      description: "Helpful service for housing, onboarding, or administrative support.",
      why: "Support offices can solve issues before they become urgent.",
      avatar: "RS",
      avatarTone: "aqua",
      trustSignals: [],
      detailLines: ["Helpful for admin, legal, onboarding, and student support."],
      cta: null,
    })),
  ];

  const planSteps = first(plan?.steps, 12).map((step, index) => ({
    cardId: `plan-step-${index}`,
    id: `plan-step-${index}`,
    title: step.action,
    kind: weekLabel(step.day_range, index),
    nodeId: Array.isArray(step.source_node_ids) ? step.source_node_ids[0] : null,
    sourceNodeIds: Array.isArray(step.source_node_ids) ? step.source_node_ids : [],
    subtitle: step.day_range || weekLabel(step.day_range, index),
    description: step.dependency_reason,
    why: "This action is sequenced to reduce friction in your first 30 days.",
    avatar: "TK",
    avatarTone: "teal",
    trustSignals: Array.isArray(step.entities) ? step.entities.slice(0, 3) : [],
    detailLines: [step.dependency_reason || null].filter(Boolean),
    cta: null,
  }));

  return {
    people: {
      title: "People who can help this week",
      description: "Mentors and peers ranked for trust, context, and practical fit.",
      items: [...mentors, ...peers],
      empty: "No people matches yet. Refresh your profile to repopulate support connections.",
    },
    events: {
      title: "Events that build belonging",
      description: "Social and cultural touchpoints connected to your destination city.",
      items: events,
      empty: "No events in this snapshot. Try refreshing profile match.",
    },
    food: {
      title: "Food and essentials",
      description: "Comfort routines matter. Start with familiar food and easy essentials.",
      items: food,
      empty: "No food nodes matched yet.",
    },
    housing: {
      title: "Housing and support",
      description: "Explore safer housing context plus support offices that can unblock paperwork.",
      items: housing,
      empty: "No housing context found yet.",
    },
    tasks: {
      title: "Plan-linked tasks",
      description: "These tasks are connected to graph nodes so you can jump directly to help.",
      items: planSteps,
      empty: "Generate your 30-day plan in Step 2 to unlock task-linked exploration.",
    },
  };
}

function weekLabel(dayRange, index) {
  const values = (String(dayRange || "").match(/\d+/g) || []).map((value) => Number(value));
  const lastDay = values.length ? values[values.length - 1] : (index + 1) * 7;
  const weekNumber = Math.min(4, Math.max(1, Math.ceil(lastDay / 7)));
  return `Week ${weekNumber}`;
}

function ExploreCard({ item, expanded, onToggle, onFocusNode }) {
  const detailLines = Array.isArray(item.detailLines) ? item.detailLines.filter(Boolean) : [];
  const hasNodeLinks = Array.isArray(item.sourceNodeIds) && item.sourceNodeIds.length > 0;

  return (
    <article className={`gb-explore-card ${expanded ? "gb-explore-card--expanded" : ""}`}>
      <div className="gb-explore-card__top">
        <div className={`gb-avatar gb-avatar--${item.avatarTone}`}>{item.avatar}</div>
        <div className="gb-explore-card__identity">
          <span className="gb-badge">{item.kind}</span>
          <h4>{item.title}</h4>
          {item.subtitle && <p>{item.subtitle}</p>}
        </div>
      </div>

      {item.trustSignals?.length > 0 && (
        <div className="gb-trust-row">
          {item.trustSignals.map((signal) => (
            <span key={`${item.cardId || item.id}-${signal}`} className="gb-chip gb-chip--soft">
              {signal}
            </span>
          ))}
        </div>
      )}

      <p className="gb-explore-card__description">{item.description}</p>

      <div className="gb-explore-card__why">
        <strong>Why this match?</strong>
        <p>{item.why}</p>
      </div>

      <div className="gb-explore-card__actions">
        {item.nodeId && (
          <button type="button" className="gb-btn gb-btn-secondary" onClick={() => onFocusNode(item.nodeId)}>
            Focus in graph
          </button>
        )}

        {item.cta?.href && (
          <a className="gb-btn gb-btn-ghost" href={item.cta.href} target="_blank" rel="noopener noreferrer">
            {item.cta.label}
          </a>
        )}

        <button type="button" className="gb-link-btn" onClick={onToggle} aria-expanded={expanded}>
          {expanded ? "Collapse" : "Expand"}
        </button>
      </div>

      {expanded && (detailLines.length > 0 || hasNodeLinks) && (
        <div className="gb-card-expand">
          <span>More details</span>
          {detailLines.map((line, index) => (
            <p key={`${item.cardId || item.id}-detail-${index}`} className="gb-card-expand__text">
              {line}
            </p>
          ))}
          {hasNodeLinks && (
            <div className="gb-chip-row">
              {item.sourceNodeIds.map((sourceId) => (
                <button
                  key={`${item.cardId || item.id}-${sourceId}`}
                  type="button"
                  className="gb-chip gb-chip--action"
                  onClick={() => onFocusNode(sourceId)}
                >
                  {sourceId}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </article>
  );
}

export default function ExploreWorkspace({
  match,
  plan,
  category,
  onCategoryChange,
  selectedNode,
  onNodeSelect,
  onClearNode,
  onPathChange,
}) {
  const [expandedId, setExpandedId] = useState(null);
  const categoryData = useMemo(() => buildCategoryData(match, plan), [match, plan]);
  const activeCategory = categoryData[category] ? category : "people";
  const active = categoryData[activeCategory];

  const nodeMap = useMemo(() => {
    return new Map((match?.subgraph?.nodes || []).map((node) => [node.id, node]));
  }, [match?.subgraph?.nodes]);

  const focusNode = (nodeId) => {
    const node = nodeMap.get(nodeId);
    if (!node) return;
    onNodeSelect(node);
  };

  return (
    <div className="gb-explore-shell">
      <section className="gb-explore-left" aria-label="Explore categories and matches">
        <div className="gb-explore-head">
          <h3>Explore Nearby</h3>
          <p>Pick a category and follow clear, human explanations for each recommendation.</p>
        </div>

        <div className="gb-pill-row" role="tablist" aria-label="Explore categories">
          {CATEGORY_OPTIONS.map((option) => (
            <button
              key={option.id}
              type="button"
              role="tab"
              aria-selected={activeCategory === option.id}
              className={`gb-pill-tab ${activeCategory === option.id ? "gb-pill-tab--active" : ""}`}
              onClick={() => {
                onCategoryChange(option.id);
                setExpandedId(null);
              }}
            >
              {option.label}
            </button>
          ))}
        </div>

        <div className="gb-explore-section-head">
          <h4>{active.title}</h4>
          <p>{active.description}</p>
        </div>

        {active.items.length > 0 ? (
          <div className="gb-explore-grid">
            {active.items.map((item, index) => {
              const cardKey = item.cardId || `${activeCategory}-${item.id || item.title}-${index}`;
              return (
              <ExploreCard
                key={cardKey}
                item={item}
                expanded={expandedId === cardKey}
                onToggle={() => setExpandedId((prev) => (prev === cardKey ? null : cardKey))}
                onFocusNode={focusNode}
              />
              );
            })}
          </div>
        ) : (
          <p className="gb-explore-empty">{active.empty}</p>
        )}
      </section>

      <section className="gb-explore-right" aria-label="Support graph">
        <div className="gb-graph-tip" role="note">
          This graph shows your support network. Click any node to see details and possible next actions.
        </div>

        <GraphCanvas
          compact
          nodes={match?.subgraph?.nodes}
          edges={match?.subgraph?.edges}
          onNodeSelect={onNodeSelect}
          selectedNodeId={selectedNode?.id}
          onPathComputed={onPathChange}
        />

        <aside className="gb-side-panel" aria-label="Node details">
          {selectedNode ? (
            <NodeDetailCard node={selectedNode} onClear={onClearNode} />
          ) : (
            <div className="gb-side-panel__empty">
              Select a graph node to understand who or what can help you next.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
