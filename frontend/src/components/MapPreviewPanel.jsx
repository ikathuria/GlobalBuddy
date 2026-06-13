/** OpenStreetMap preview — no API key. Embeds a marker map when lat/lon are
 * known, otherwise links out to an OpenStreetMap search for the query text. */

function osmSearchUrl(query) {
  return `https://www.openstreetmap.org/search?query=${encodeURIComponent(query)}`;
}

function osmEmbedUrl(lat, lon) {
  const d = 0.008;
  const bbox = `${lon - d},${lat - d},${lon + d},${lat + d}`;
  return `https://www.openstreetmap.org/export/embed.html?bbox=${encodeURIComponent(bbox)}&layer=mapnik&marker=${lat},${lon}`;
}

function queryFromLink(mapsLink) {
  const link = (mapsLink || "").trim();
  if (!link) return "";
  try {
    return new URL(link).searchParams.get("query") || "";
  } catch {
    return "";
  }
}

export default function MapPreviewPanel({ latitude, longitude, mapsLink, mapsQuery, title }) {
  const lat = Number(latitude);
  const lon = Number(longitude);
  const hasCoords = Number.isFinite(lat) && Number.isFinite(lon) && (lat !== 0 || lon !== 0);
  const query = (mapsQuery || queryFromLink(mapsLink) || title || "").trim();

  if (!hasCoords && !query) return null;

  return (
    <div className="gb-map-preview" aria-label={title || "Map preview"}>
      <div className="gb-map-preview__label">Map preview · OpenStreetMap</div>
      {hasCoords ? (
        <iframe
          title={title || "Location map"}
          className="gb-map-preview__frame"
          src={osmEmbedUrl(lat, lon)}
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        />
      ) : (
        <a
          className="gb-btn gb-btn-secondary gb-map-preview__link"
          href={osmSearchUrl(query)}
          target="_blank"
          rel="noopener noreferrer"
        >
          View “{title || query}” on OpenStreetMap
        </a>
      )}
    </div>
  );
}
