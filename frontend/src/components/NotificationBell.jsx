import { useCallback, useEffect, useRef, useState } from "react";
import client from "../api/client.js";
import { useAuth } from "../contexts/AuthContext.jsx";

const POLL_MS = 30_000;

function timeAgo(iso) {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "";
  const mins = Math.round((Date.now() - then) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
}

export default function NotificationBell() {
  const { user, accessToken } = useAuth();
  const enabled = Boolean(user && accessToken);

  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const [open, setOpen] = useState(false);
  const lastSeenId = useRef(null);

  const refresh = useCallback(async () => {
    try {
      const res = await client.get("/v1/notifications");
      const next = res.data.items || [];
      setItems(next);
      setUnread(res.data.unread || 0);

      // Fire a local browser notification for genuinely new items (opt-in).
      const newest = next[0];
      if (
        newest &&
        newest.id !== lastSeenId.current &&
        lastSeenId.current !== null &&
        typeof Notification !== "undefined" &&
        Notification.permission === "granted"
      ) {
        new Notification(newest.title, { body: newest.body });
      }
      if (newest) lastSeenId.current = newest.id;
    } catch {
      // Silent — polling will retry.
    }
  }, []);

  useEffect(() => {
    if (!enabled) return undefined;
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [enabled, refresh]);

  if (!enabled) return null;

  const markRead = async (n) => {
    if (!n.read) {
      setUnread((u) => Math.max(0, u - 1));
      setItems((prev) => prev.map((i) => (i.id === n.id ? { ...i, read: true } : i)));
      try {
        await client.post(`/v1/notifications/${encodeURIComponent(n.id)}/read`);
      } catch {
        /* ignore */
      }
    }
  };

  const markAll = async () => {
    setUnread(0);
    setItems((prev) => prev.map((i) => ({ ...i, read: true })));
    try {
      await client.post("/v1/notifications/read-all");
    } catch {
      /* ignore */
    }
  };

  const enableAlerts = () => {
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      Notification.requestPermission();
    }
  };

  const canPrompt = typeof Notification !== "undefined" && Notification.permission === "default";

  return (
    <div className="gb-bell">
      <button
        type="button"
        className="gb-bell__btn"
        aria-label={`Notifications${unread ? `, ${unread} unread` : ""}`}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
      >
        🔔
        {unread > 0 && <span className="gb-bell__badge">{unread > 9 ? "9+" : unread}</span>}
      </button>

      {open && (
        <div className="gb-bell__panel" role="menu">
          <div className="gb-bell__head">
            <strong>Notifications</strong>
            {items.some((i) => !i.read) && (
              <button type="button" className="gb-link-btn" onClick={markAll}>Mark all read</button>
            )}
          </div>

          {canPrompt && (
            <button type="button" className="gb-bell__enable" onClick={enableAlerts}>
              Enable browser alerts
            </button>
          )}

          {items.length === 0 ? (
            <p className="gb-bell__empty">No notifications yet.</p>
          ) : (
            <ul className="gb-bell__list">
              {items.map((n) => (
                <li key={n.id}>
                  <button
                    type="button"
                    className={`gb-bell__item ${n.read ? "" : "gb-bell__item--unread"}`}
                    onClick={() => markRead(n)}
                  >
                    <strong>{n.title}</strong>
                    {n.body && <p>{n.body}</p>}
                    <span className="gb-bell__time">{timeAgo(n.created_at)}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
