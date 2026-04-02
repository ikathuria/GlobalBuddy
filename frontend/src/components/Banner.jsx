export default function Banner({ type = "success", message, onDismiss }) {
  if (!message) return null;

  const className = type === "error" ? "gb-banner gb-banner--error" : "gb-banner gb-banner--success";

  return (
    <div className={className} role="status">
      <span>{message}</span>
      {onDismiss && (
        <button type="button" className="gb-banner__close" onClick={onDismiss} aria-label="Dismiss">
          x
        </button>
      )}
    </div>
  );
}
