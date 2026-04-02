import axios from "axios";

/** Resolved API origin (Vite injects VITE_* at dev server start — restart `npm run dev` after changing .env.local). */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  // Do not set Content-Type globally: `Content-Type: application/json` on GET triggers a CORS preflight
  // and can make health checks fail in the browser while curl still works. Axios sets JSON Content-Type
  // automatically for POST/PUT bodies.
  timeout: Number(import.meta.env.VITE_API_TIMEOUT_MS ?? 180_000),
});

export default client;
