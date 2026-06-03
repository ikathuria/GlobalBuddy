import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { neonAuthClient, neonAuthConfigured } from "../auth/neonAuth.js";
import { clearAuthToken, getAuthToken, setAuthToken } from "../auth/tokenStore.js";

const USER_STORAGE_KEY = "gb_user";
const AuthContext = createContext(null);

function storedUser() {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    localStorage.removeItem(USER_STORAGE_KEY);
    return null;
  }
}

function persistUser(user) {
  if (!user) {
    localStorage.removeItem(USER_STORAGE_KEY);
    return;
  }
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
}

function safeRandomId() {
  return globalThis.crypto?.randomUUID?.() ?? `local-${Date.now()}`;
}

function localUser({ email, fullName }) {
  return {
    id: safeRandomId(),
    email,
    full_name: fullName || email.split("@")[0],
    stage: "newcomer",
  };
}

function resultData(result) {
  return result?.data ?? result ?? {};
}

function extractToken(result) {
  const data = resultData(result);
  return (
    data?.session?.token ||
    data?.session?.access_token ||
    data?.session?.accessToken ||
    data?.token ||
    data?.access_token ||
    data?.accessToken ||
    ""
  );
}

function extractUser(result, fallback = {}) {
  const data = resultData(result);
  const user = data?.user || data?.session?.user || null;
  if (!user && !fallback.email) return null;
  return {
    id: String(user?.id || user?.sub || user?.user_id || fallback.id || safeRandomId()),
    email: user?.email || fallback.email || "",
    full_name: user?.name || user?.full_name || fallback.fullName || fallback.email?.split("@")[0] || "",
    stage: user?.stage || fallback.stage || "newcomer",
  };
}

function authError(error, fallback = "Authentication failed.") {
  if (!error) return null;
  if (typeof error === "string") return { message: error };
  return { message: error.message || error.detail || fallback };
}

async function currentNeonSession(fallback = {}) {
  if (!neonAuthClient) return { user: null, token: "" };
  const sessionResult = await neonAuthClient.getSession();
  if (sessionResult?.error) {
    return { user: null, token: "", error: authError(sessionResult.error) };
  }
  return {
    user: extractUser(sessionResult, fallback),
    token: extractToken(sessionResult),
  };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => storedUser());
  const [accessToken, setAccessTokenState] = useState(() => getAuthToken());
  const [loading, setLoading] = useState(true);

  const applySession = useCallback((nextUser, token = "") => {
    persistUser(nextUser);
    setAuthToken(token);
    setUser(nextUser);
    setAccessTokenState(token);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function hydrate() {
      if (!neonAuthConfigured) {
        setLoading(false);
        return;
      }

      try {
        const session = await currentNeonSession();
        if (cancelled) return;
        if (session.user) {
          applySession(session.user, session.token);
        } else {
          applySession(null, "");
        }
      } catch {
        if (!cancelled) applySession(null, "");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    hydrate();
    return () => {
      cancelled = true;
    };
  }, [applySession]);

  const signUp = useCallback(async ({ email, password, fullName }) => {
    if (!neonAuthClient) {
      const nextUser = localUser({ email, fullName });
      applySession(nextUser, "");
      return { user: nextUser, error: null };
    }

    const result = await neonAuthClient.signUp.email({ email, password, name: fullName || email });
    if (result?.error) return { user: null, error: authError(result.error) };

    const session = await currentNeonSession({ email, fullName });
    if (session.error) return { user: null, error: session.error };

    const nextUser = session.user || extractUser(result, { email, fullName });
    const token = session.token || extractToken(result);
    if (!nextUser || !token) {
      return { user: null, error: { message: "Account created. Check your email to finish signing in." } };
    }

    applySession(nextUser, token);
    return { user: nextUser, error: null };
  }, [applySession]);

  const signIn = useCallback(async ({ email, password }) => {
    if (!neonAuthClient) {
      const nextUser = localUser({ email });
      applySession(nextUser, "");
      return { user: nextUser, error: null };
    }

    const result = await neonAuthClient.signIn.email({ email, password });
    if (result?.error) return { user: null, error: authError(result.error) };

    const session = await currentNeonSession({ email });
    if (session.error) return { user: null, error: session.error };

    const nextUser = session.user || extractUser(result, { email });
    const token = session.token || extractToken(result);
    if (!nextUser || !token) {
      return { user: null, error: { message: "Signed in, but no session token was returned." } };
    }

    applySession(nextUser, token);
    return { user: nextUser, error: null };
  }, [applySession]);

  const signInWithLinkedIn = useCallback(async () => {
    if (!neonAuthClient) {
      return { user: null, error: { message: "LinkedIn sign-in requires Neon Auth to be configured." } };
    }

    const result = await neonAuthClient.signIn.social({
      provider: "linkedin",
      callbackURL: "/dashboard",
    });
    if (result?.error) return { user: null, error: authError(result.error) };
    return { user: null, error: null };
  }, []);

  const signOut = useCallback(async () => {
    if (neonAuthClient) {
      try {
        await neonAuthClient.signOut();
      } catch {
        // Local cleanup still matters if the remote sign-out request fails.
      }
    }
    clearAuthToken();
    applySession(null, "");
  }, [applySession]);

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        loading,
        authConfigured: neonAuthConfigured,
        signIn,
        signUp,
        signInWithLinkedIn,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
