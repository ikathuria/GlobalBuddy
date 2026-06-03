import { createAuthClient } from "@neondatabase/neon-js/auth";

export const neonAuthUrl = import.meta.env.VITE_NEON_AUTH_URL ?? "";
export const neonAuthConfigured = Boolean(neonAuthUrl.trim());

export const neonAuthClient = neonAuthConfigured ? createAuthClient(neonAuthUrl) : null;
