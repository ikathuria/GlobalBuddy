import { useEffect, useState } from "react";
import GraphCanvas from "./GraphCanvas.jsx";
import NodeDetailCard from "./NodeDetailCard.jsx";

const CATEGORY_OPTIONS = [
  { id: "people", label: "People" },
  { id: "community", label: "Community" },
  { id: "worship", label: "Worship" },
  { id: "your-culture", label: "Your Culture" },
  { id: "other-culture", label: "Other Culture" },
  { id: "resources", label: "Resources" },
  { id: "places", label: "Places to Visit" },
  { id: "groceries", label: "Groceries" },
  { id: "housing", label: "Housing" },
  { id: "transit", label: "Transit" },
];

function textValue(value) {
  if (!value) return "";
  if (Array.isArray(value)) return value.join(" ");
  return String(value);
}

function mapsHref(item) {
  const direct = (item.maps_link || "").trim();
  if (direct) return direct;
  const query = (item.maps_query || item.address || item.location || item.name || "").trim();
  if (!query) return "";
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

function toKeywords(match) {
  const profile = match?.evidence_bundle?.student_profile || {};
  const raw = [
    profile.country_of_origin,
    profile.home_city,
    profile.cultural_background,
    profile.religion_or_observance,
    profile.diet,
    textValue(profile.needs),
    textValue(profile.interests),
  ]
    .join(" ")
    .toLowerCase();

  return raw
    .split(/[^a-z0-9]+/)
    .filter((token) => token.length > 3)
    .slice(0, 16);
}

function isYourCulture(item, keywords) {
  if (!keywords.length) return false;
  const haystack = [item.name, item.category, item.notes, item.why_recommended, item.location]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return keywords.some((keyword) => haystack.includes(keyword));
}

function emailHref(email, name) {
  if (!email) return "";
  const subject = encodeURIComponent(`Globaldost intro | ${name || "New connection"}`);
  return `mailto:${encodeURIComponent(email)}?subject=${subject}`;
}

function socialHref(value, platform) {
  const raw = (value || "").trim();
  if (!raw) return "";
  if (/^https?:\/\//i.test(raw)) return raw;
  if (platform === "instagram") {
    const handle = raw.startsWith("@") ? raw.slice(1) : raw;
    return `https://www.instagram.com/${encodeURIComponent(handle)}`;
  }
  return raw;
}

function mentorToCard(mentor) {
  return {
    id: mentor.id,
    badge: "Mentor",
    title: mentor.name,
    meta: (mentor.match_reasons || []).join(" | ") || "Graph-ranked mentor match",
    body: mentor.why_this_match || mentor.connect_hint || "Strong match for your profile.",
    actionLabel: mentor.email ? "Email" : mentor.linkedin_url ? "LinkedIn" : "View profile",
    actionHref: mentor.email ? emailHref(mentor.email, mentor.name) : mentor.linkedin_url || "",
    profile: {
      role: "Mentor",
      name: mentor.name,
      email: mentor.email || "",
      linkedin_url: mentor.linkedin_url || "",
      instagram_url: mentor.instagram_url || "",
      confidence_score: mentor.confidence_score ?? mentor.match_score ?? null,
      trust_score: mentor.trust_score ?? null,
      languages: mentor.languages || [],
      match_reasons: mentor.match_reasons || [],
      connect_hint: mentor.connect_hint || "",
      why_this_match: mentor.why_this_match || "",
    },
  };
}

function peerToCard(peer) {
  return {
    id: peer.id,
    badge: "Peer",
    title: peer.name,
    meta: [peer.neighborhood, peer.university].filter(Boolean).join(" | ") || "Peer nearby",
    body: peer.connect_hint || "Reach out for local guidance.",
    actionLabel: peer.email ? "Email" : "Open",
    actionHref: peer.email ? emailHref(peer.email, peer.name) : "",
    profile: {
      role: "Peer",
      name: peer.name,
      email: peer.email || "",
      linkedin_url: peer.linkedin_url || "",
      instagram_url: peer.instagram_url || "",
      university: peer.university || "",
      neighborhood: peer.neighborhood || "",
      connect_hint: peer.connect_hint || "",
    },
  };
}

function PersonProfileModal({ item, onClose }) {
  useEffect(() => {
    if (!item) return undefined;
    const onKeyDown = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [item, onClose]);

  if (!item?.profile) return null;

  const p = item.profile;
  const linkedinHref = socialHref(p.linkedin_url, "linkedin");
  const instagramHref = socialHref(p.instagram_url, "instagram");

  return (
    <div className="gb-profile-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <aside
        className="gb-profile-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="person-profile-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="gb-profile-modal__head">
          <div>
            <p className="gb-profile-modal__eyebrow">{p.role} profile</p>
            <h3 id="person-profile-title">{p.name}</h3>
          </div>
          <button type="button" className="gb-banner__close" onClick={onClose} aria-label="Close profile">
            ×
          </button>
        </div>

        {(p.why_this_match || p.connect_hint) && (
          <p className="gb-profile-modal__summary">{p.why_this_match || p.connect_hint}</p>
        )}

        <div className="gb-profile-modal__grid">
          {p.email && (
            <div className="gb-profile-modal__item">
              <span>Email</span>
              <a href={`mailto:${encodeURIComponent(p.email)}`}>{p.email}</a>
            </div>
          )}
          {p.university && (
            <div className="gb-profile-modal__item">
              <span>University</span>
              <strong>{p.university}</strong>
            </div>
          )}
          {p.neighborhood && (
            <div className="gb-profile-modal__item">
              <span>Neighborhood</span>
              <strong>{p.neighborhood}</strong>
            </div>
          )}
          {p.confidence_score != null && (
            <div className="gb-profile-modal__item">
              <span>Confidence</span>
              <strong>{Math.round(Number(p.confidence_score) * 100)}%</strong>
            </div>
          )}
          {p.trust_score != null && (
            <div className="gb-profile-modal__item">
              <span>Trust score</span>
              <strong>{Number(p.trust_score).toFixed(2)}</strong>
            </div>
          )}
          {Array.isArray(p.languages) && p.languages.length > 0 && (
            <div className="gb-profile-modal__item gb-profile-modal__item--full">
              <span>Languages</span>
              <strong>{p.languages.join(" | ")}</strong>
            </div>
          )}
          {Array.isArray(p.match_reasons) && p.match_reasons.length > 0 && (
            <div className="gb-profile-modal__item gb-profile-modal__item--full">
              <span>Why this person</span>
              <strong>{p.match_reasons.join(" | ")}</strong>
            </div>
          )}
        </div>

        <div className="gb-profile-modal__actions">
          {p.email && (
            <a className="gb-btn gb-btn-primary" href={emailHref(p.email, p.name)}>
              Email now
            </a>
          )}
          {linkedinHref && (
            <a className="gb-btn gb-btn-secondary" href={linkedinHref} target="_blank" rel="noopener noreferrer">
              LinkedIn
            </a>
          )}
          {instagramHref && (
            <a className="gb-btn gb-btn-secondary" href={instagramHref} target="_blank" rel="noopener noreferrer">
              Instagram
            </a>
          )}
        </div>
      </aside>
    </div>
  );
}

function localToCard(item, badge, fallbackBody) {
  return {
    id: item.id,
    badge,
    title: item.name,
    meta: [item.neighborhood, item.address, item.location].filter(Boolean).join(" | ") || "Nearby",
    body: item.why_recommended || item.notes || item.summary || fallbackBody,
    actionLabel: mapsHref(item) ? "Open in Maps" : "View",
    actionHref: mapsHref(item),
  };
}

function resourceToCard(resource) {
  return {
    id: resource.id,
    badge: "Resource",
    title: resource.name,
    meta: resource.resource_type || "Support",
    body: "Support service available in your city context.",
    actionLabel: "View",
    actionHref: "",
  };
}

function buildCategoryData(match) {
  const mentors = match?.mentors_top3 || [];
  const peers = match?.peers_nearby || [];
  const worship = match?.places_of_worship || [];
  const groceries = match?.grocery_stores || [];
  const housing = match?.housing_areas || [];
  const places = match?.exploration_spots || [];
  const transit = match?.transit_tips || [];
  const resources = match?.resources || [];
  const events = match?.community_events || [];

  const keywords = toKeywords(match);
  const yourCultureEvents = events.filter((item) => isYourCulture(item, keywords));
  const otherCultureEvents = events.filter((item) => !isYourCulture(item, keywords));

  return {
    people: {
      title: "People nearby",
      description: "Mentors and peers matched from your graph profile.",
      items: [...mentors.map(mentorToCard), ...peers.map(peerToCard)],
    },
    community: {
      title: "Community highlights",
      description: "Quick snapshot of local events, resources, and transit tips.",
      items: [
        ...events.slice(0, 4).map((item) => localToCard(item, "Event", "Community event in your area.")),
        ...resources.slice(0, 3).map(resourceToCard),
        ...transit.slice(0, 3).map((item) => localToCard(item, "Transit", "Transit tip near your campus.")),
      ],
    },
    worship: {
      title: "Worship and belonging",
      description: "Places connected to faith and spiritual community.",
      items: worship.map((item) => localToCard(item, "Worship", "Faith-based gathering point.")),
    },
    "your-culture": {
      title: "Your culture",
      description: "Events and community spots that resemble your background.",
      items: [
        ...yourCultureEvents.map((item) => localToCard(item, "Culture", "Cultural event tied to your profile.")),
        ...worship.filter((item) => isYourCulture(item, keywords)).map((item) => localToCard(item, "Worship", "Shared cultural context.")),
      ],
    },
    "other-culture": {
      title: "Other cultures",
      description: "Broaden your network with nearby cross-cultural events.",
      items: otherCultureEvents.map((item) => localToCard(item, "Event", "Cross-cultural event to explore.")),
    },
    resources: {
      title: "Resources",
      description: "Support services you can use this week.",
      items: resources.map(resourceToCard),
    },
    places: {
      title: "Places to visit",
      description: "Comfort spots and social places around your target city.",
      items: places.map((item) => localToCard(item, "Explore", "Popular local place to explore.")),
    },
    groceries: {
      title: "Groceries and essentials",
      description: "Stores for everyday basics.",
      items: groceries.map((item) => localToCard(item, "Grocery", "Store for essentials and routine shopping.")),
    },
    housing: {
      title: "Housing areas",
      description: "Neighborhood options to evaluate while settling in.",
      items: housing.map((item) => localToCard(item, "Housing", "Area connected to your profile needs.")),
    },
    transit: {
      title: "Transit",
      description: "Mobility guidance to move safely and cheaply.",
      items: transit.map((item) => localToCard(item, "Transit", "Transit route or station tip.")),
    },
  };
}

export default function ExploreWorkspace({
  match,
  category,
  onCategoryChange,
  selectedNode,
  onNodeSelect,
  onClearNode,
}) {
  const [expandedPerson, setExpandedPerson] = useState(null);
  const categoryData = buildCategoryData(match);
  const activeCategory = categoryData[category] ? category : "people";
  const active = categoryData[activeCategory];

  useEffect(() => {
    if (activeCategory !== "people") {
      setExpandedPerson(null);
    }
  }, [activeCategory]);

  return (
    <div className="gb-explore-layout">
      <section className="gb-card gb-explore-panel" aria-label="Explore categories">
        <div className="gb-explore-panel__top">
          <h2 className="gb-card-title--plain">Explore mode</h2>
          <p className="gb-explore-panel__copy">
            Choose what you want to focus on. Content stays compact and scrolls sideways so the page does not overflow.
          </p>
        </div>

        <label className="gb-field gb-explore-select">
          <span>Explore category</span>
          <select value={activeCategory} onChange={(event) => onCategoryChange(event.target.value)}>
            {CATEGORY_OPTIONS.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <div className="gb-explore-panel__headline">
          <h3>{active.title}</h3>
          <p>{active.description}</p>
        </div>

        {active.items.length > 0 ? (
          <div className="gb-carousel" role="region" aria-label={`${active.title} carousel`}>
            <div className="gb-carousel-track">
              {active.items.map((item, index) => (
                <article key={item.id || `${activeCategory}-${item.title}-${index}`} className="gb-carousel-card">
                  <div className="gb-carousel-card__head">
                    <span className="gb-badge">{item.badge}</span>
                    <h4>{item.title}</h4>
                  </div>
                  {item.meta && <p className="gb-carousel-card__meta">{item.meta}</p>}
                  {item.body && <p className="gb-carousel-card__body">{item.body}</p>}
                  {(item.actionHref || item.profile) && (
                    <div className="gb-carousel-card__actions">
                      {item.actionHref && (
                        <a className="gb-btn gb-btn-secondary gb-carousel-card__action" href={item.actionHref} target="_blank" rel="noopener noreferrer">
                          {item.actionLabel}
                        </a>
                      )}
                      {item.profile && (
                        <button type="button" className="gb-btn gb-btn-primary gb-carousel-card__action" onClick={() => setExpandedPerson(item)}>
                          Expand profile
                        </button>
                      )}
                    </div>
                  )}
                </article>
              ))}
            </div>
          </div>
        ) : (
          <p className="gb-explore-empty">
            No items in this category yet. Try another tab, or refresh your profile match to pull a new evidence set.
          </p>
        )}
      </section>

      <div className="gb-explore-graph">
        <GraphCanvas
          compact
          nodes={match?.subgraph?.nodes}
          edges={match?.subgraph?.edges}
          onNodeSelect={onNodeSelect}
          selectedNodeId={selectedNode?.id}
        />
        <NodeDetailCard node={selectedNode} onClear={onClearNode} />
      </div>
      <PersonProfileModal item={expandedPerson} onClose={() => setExpandedPerson(null)} />
    </div>
  );
}
