CREATE TABLE IF NOT EXISTS app_sessions (
  session_id text PRIMARY KEY,
  payload jsonb NOT NULL,
  expires_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_app_sessions_expires_at
ON app_sessions (expires_at);

CREATE TRIGGER trg_app_sessions_updated_at
BEFORE UPDATE ON app_sessions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
