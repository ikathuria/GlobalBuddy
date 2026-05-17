import { createContext, useCallback, useContext, useEffect, useState } from "react";

// Will be replaced with Supabase client once credentials are configured.
// For now this stub keeps auth state in localStorage so the UI is fully functional.

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("gb_user");
      if (stored) setUser(JSON.parse(stored));
    } catch {
      localStorage.removeItem("gb_user");
    }
    setLoading(false);
  }, []);

  const signUp = useCallback(async ({ email, password, fullName }) => {
    // Stub: will delegate to Supabase Auth once SUPABASE_URL is configured.
    const newUser = { id: crypto.randomUUID(), email, full_name: fullName, stage: "newcomer" };
    localStorage.setItem("gb_user", JSON.stringify(newUser));
    setUser(newUser);
    return { user: newUser, error: null };
  }, []);

  const signIn = useCallback(async ({ email, password }) => {
    // Stub: replace with supabase.auth.signInWithPassword({ email, password })
    const mockUser = { id: crypto.randomUUID(), email, full_name: email.split("@")[0], stage: "newcomer" };
    localStorage.setItem("gb_user", JSON.stringify(mockUser));
    setUser(mockUser);
    return { user: mockUser, error: null };
  }, []);

  const signOut = useCallback(async () => {
    localStorage.removeItem("gb_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
