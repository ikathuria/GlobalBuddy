import { useEffect, useMemo, useState } from "react";
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

function contactHref(value, type) {
  const raw = String(value || "").trim();
  if (!raw) return "";

  if (type === "email") {
    return `mailto:${encodeURIComponent(raw)}`;
  }

  if (/^https?:\/\//i.test(raw)) {
    return raw;
  }

  if (type === "instagram") {
    const handle = raw.startsWith("@") ? raw.slice(1) : raw;
    return `https://www.instagram.com/${encodeURIComponent(handle)}`;
  }

  if (type === "linkedin") {
    return `https://www.linkedin.com/in/${encodeURIComponent(raw.replace(/^@/, ""))}`;
  }

  if (type === "phone") {
    return `tel:${raw.replace(/\s+/g, "")}`;
  }

  return raw;
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
    isPerson: true,
    profile: {
      role: "Mentor",
      email: mentor.email || "",
      linkedin_url: mentor.linkedin_url || "",
      instagram_url: mentor.instagram_url || "",
      other_social_url: mentor.other_social_url || "",
      phone: mentor.phone || "",
      languages: mentor.languages || [],
      match_reasons: mentor.match_reasons || [],
      trust_score: mentor.trust_score,
      confidence_score: mentor.confidence_score ?? mentor.match_score,
      connect_hint: mentor.connect_hint || "",
      why_this_match: mentor.why_this_match || "",
    },
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
    isPerson: true,
    profile: {
      role: "Peer",
      email: peer.email || "",
      linkedin_url: peer.linkedin_url || "",
      instagram_url: peer.instagram_url || "",
      other_social_url: peer.other_social_url || "",
      phone: peer.phone || "",
      neighborhood: peer.neighborhood || "",
      university: peer.university || "",
      connect_hint: peer.connect_hint || "",
      why_this_match: "Shared destination context can reduce first-week overwhelm.",
    },
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

        <button
          type="button"
          className="gb-link-btn"
          onClick={onToggle}
          aria-expanded={item.isPerson ? undefined : expanded}
        >
          {item.isPerson ? "Expand profile" : expanded ? "Collapse" : "Expand"}
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

function PersonProfileModal({ item, onClose }) {
  useEffect(() => {
    if (!item) return undefined;
    const onKeyDown = (event) => {
      if (event.key === "Escape") onClose?.();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [item, onClose]);

  if (!item?.isPerson || !item?.profile) return null;

  const profile = item.profile;
  const contactOptions = [
    { key: "email", label: "Email", href: contactHref(profile.email, "email") },
    { key: "linkedin", label: "LinkedIn", href: contactHref(profile.linkedin_url, "linkedin") },
    { key: "instagram", label: "Instagram", href: contactHref(profile.instagram_url, "instagram") },
    { key: "other", label: "Other Social", href: contactHref(profile.other_social_url, "url") },
    { key: "phone", label: "Call", href: contactHref(profile.phone, "phone") },
  ].filter((option) => option.href);

  return (
    <div
      className="gb-profile-modal-backdrop"
      role="presentation"
      onMouseDown={(event) => event.target === event.currentTarget && onClose?.()}
    >
      <aside
        className="gb-profile-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="person-profile-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="gb-profile-modal__head">
          <div>
            <p className="gb-profile-modal__eyebrow">{profile.role} profile</p>
            <h3 id="person-profile-title">{item.title}</h3>
            {item.subtitle && <p className="gb-profile-modal__subtitle">{item.subtitle}</p>}
          </div>
          <button type="button" className="gb-banner__close" onClick={onClose} aria-label="Close profile">
            x
          </button>
        </div>

        <p className="gb-profile-modal__summary">{item.description}</p>

        <div className="gb-profile-modal__grid">
          {profile.university && (
            <div className="gb-profile-modal__item">
              <span>University</span>
              <strong>{profile.university}</strong>
            </div>
          )}
          {profile.neighborhood && (
            <div className="gb-profile-modal__item">
              <span>Neighborhood</span>
              <strong>{profile.neighborhood}</strong>
            </div>
          )}
          {profile.confidence_score != null && (
            <div className="gb-profile-modal__item">
              <span>Match confidence</span>
              <strong>{toPct(profile.confidence_score)}</strong>
            </div>
          )}
          {profile.trust_score != null && (
            <div className="gb-profile-modal__item">
              <span>Trust score</span>
              <strong>{Number(profile.trust_score).toFixed(2)}</strong>
            </div>
          )}
          {Array.isArray(profile.languages) && profile.languages.length > 0 && (
            <div className="gb-profile-modal__item gb-profile-modal__item--full">
              <span>Languages</span>
              <strong>{profile.languages.join(" | ")}</strong>
            </div>
          )}
          {Array.isArray(profile.match_reasons) && profile.match_reasons.length > 0 && (
            <div className="gb-profile-modal__item gb-profile-modal__item--full">
              <span>Why this match</span>
              <strong>{profile.match_reasons.join(" | ")}</strong>
            </div>
          )}
          {(profile.why_this_match || profile.connect_hint) && (
            <div className="gb-profile-modal__item gb-profile-modal__item--full">
              <span>Guidance</span>
              <strong>{profile.why_this_match || profile.connect_hint}</strong>
            </div>
          )}
        </div>

        <div className="gb-profile-modal__actions">
          {contactOptions.length > 0 ? (
            contactOptions.map((option) => (
              <a
                key={`${item.cardId}-${option.key}`}
                className="gb-btn gb-btn-primary"
                href={option.href}
                target={option.key === "email" || option.key === "phone" ? undefined : "_blank"}
                rel={option.key === "email" || option.key === "phone" ? undefined : "noopener noreferrer"}
              >
                {option.label}
              </a>
            ))
          ) : (
            <span className="gb-profile-modal__no-contacts">No contact details shared yet.</span>
          )}
        </div>
      </aside>
    </div>
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
  const [activePerson, setActivePerson] = useState(null);
  const categoryData = useMemo(() => buildCategoryData(match, plan), [match, plan]);
  const activeCategory = categoryData[category] ? category : "people";
  const active = categoryData[activeCategory];

  useEffect(() => {
    if (activeCategory !== "people") {
      setActivePerson(null);
    }
  }, [activeCategory]);

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
                setActivePerson(null);
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
                expanded={item.isPerson ? false : expandedId === cardKey}
                onToggle={() => {
                  if (item.isPerson) {
                    setActivePerson(item);
                    return;
                  }
                  setExpandedId((prev) => (prev === cardKey ? null : cardKey));
                }}
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
      <PersonProfileModal item={activePerson} onClose={() => setActivePerson(null)} />
    </div>
  );
}
