-- Social layer (M11): a real user's outgoing connection / intro requests.
--
-- These target Markdown graph entities (seed mentors and peers identified by
-- node id), recorded against the authenticated requester. The user<->user
-- `connections` table from 001 is reserved for the future real social graph
-- (M13 mentor system, M14 notifications); this table powers the MVP where the
-- people surfaced in Explore are seed graph nodes, not Neon user rows.

CREATE TABLE IF NOT EXISTS social_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  requester_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  kind text NOT NULL CHECK (kind IN ('connection', 'intro')),
  target_node_id text NOT NULL,
  target_name text NOT NULL DEFAULT '',
  target_role text NOT NULL DEFAULT '',
  message text NOT NULL DEFAULT '',
  status text NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'accepted', 'declined')),
  email_sent boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (requester_id, kind, target_node_id)
);

CREATE INDEX IF NOT EXISTS idx_social_requests_requester_created
ON social_requests (requester_id, created_at DESC);

CREATE TRIGGER trg_social_requests_updated_at
BEFORE UPDATE ON social_requests
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
