/** Static Google Maps embed from graph `maps_query` or `query` in `maps_link` — no API key. */

function embedSrc(mapsLink, mapsQuery) {
  const q = (mapsQuery || "").trim();
  if (q) {
    return `https://maps.google.com/maps?q=${encodeURIComponent(q)}&hl=en&z=14&output=embed`;
  }
  const link = (mapsLink || "").trim();
  if (!link) return null;
  try {
    const u = new URL(link);
    const qp = u.searchParams.get("query");
    if (qp) {
      return `https://maps.google.com/maps?q=${encodeURIComponent(qp)}&hl=en&z=14&output=embed`;
    }
  } catch {
    return null;
  }
  return null;
}

export default function MapPreviewPanel({ mapsLink, mapsQuery, title }) {
  const src = embedSrc(mapsLink, mapsQuery);
  if (!src) return null;
  return (
    <div className="gb-map-preview" aria-label={title || "Map preview"}>
      <div className="gb-map-preview__label">Map preview</div>
      <iframe title={title || "Location map"} className="gb-map-preview__frame" src={src} loading="lazy" referrerPolicy="no-referrer-when-downgrade" />
    </div>
  );
}
