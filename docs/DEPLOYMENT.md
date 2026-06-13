# Deployment

Globalदोस्त is two deployables: the **Vite frontend** (static) and the
**FastAPI backend** (Python web service), backed by **Neon Postgres** + **Neon
Auth**. Config files in the repo make the backend deploy reproducible:

- `backend/Procfile`, `backend/railway.toml`, `backend/runtime.txt` — Railway/Heroku-style
- `render.yaml` — Render blueprint for both services
- `frontend/vercel.json` — Vercel SPA config (rewrites all routes to `index.html`)

> Status: config is committed and the build is verified locally (`npm run build`,
> `pytest`, `validate_graph`). Actual provisioning requires your Neon, AI-provider,
> Vercel, and Railway/Render accounts and secrets — follow the steps below.

## 1. Neon (database + auth)

1. Create a Neon project. Copy the **pooled** (`DATABASE_URL`) and **direct**
   (`DATABASE_URL_UNPOOLED`) connection strings.
2. Enable **Neon Auth**; copy `NEON_AUTH_URL` and the JWKS URL (`NEON_AUTH_JWKS_URL`).
   Enable the LinkedIn social provider if using LinkedIn login.
3. Apply migrations against the direct URL:
   ```bash
   cd backend
   DATABASE_URL_UNPOOLED="<direct url>" python -m app.db.migrate
   ```
   This applies `001`–`003` (profiles, sessions, social_requests) idempotently.

## 2. Backend — Railway or Render

**Railway:** New project → deploy from repo → set service **Root Directory** to
`backend`. Railway reads `railway.toml`. Add env vars (below) in the service
**Variables** tab.

**Render:** New → **Blueprint** → point at the repo. `render.yaml` provisions the
API and static site. Fill the `sync: false` secrets in the dashboard.

Backend env vars:

| Var | Value |
|---|---|
| `AUTH_REQUIRED` | `true` |
| `CORS_ORIGINS` | your frontend URL (e.g. `https://globaldost.vercel.app`) |
| `DATABASE_URL`, `DATABASE_URL_UNPOOLED` | from Neon |
| `NEON_AUTH_URL`, `NEON_AUTH_JWKS_URL` | from Neon Auth |
| `GEMINI_API_KEY` (and/or `GROQ_API_KEY`) | AI provider |
| `RESEND_API_KEY` | optional — intro emails; without it intros still record |
| `LINKEDIN_CLIENT_ID/SECRET` | optional — LinkedIn login |

Verify: `GET /health`, `GET /health/graph`, `GET /health/providers`.

## 3. Frontend — Vercel

1. Import the repo; set **Root Directory** to `frontend`. `vercel.json` handles
   the build and SPA rewrites.
2. Set env vars: `VITE_API_BASE_URL` (the backend URL) and `VITE_NEON_AUTH_URL`.
3. Redeploy after changing env (Vite inlines `VITE_*` at build time).

## 4. Post-deploy smoke test

Sign up → onboarding → generate plan → explore → chat → send a connection/intro
request → open the feed and save an item → check the notification bell.

## Not yet automated
- Custom domain (set in Vercel once available).
- Scheduled jobs (weekly digest, reminders) — add a Railway cron or `pg_cron`.
- See PLAN.md "Notifications scope" and "Mentor merge & rating scope" for deferred work.
