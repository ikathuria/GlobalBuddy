import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext.jsx";

export default function AuthPage() {
  const { signIn, signUp, user } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Already logged in — redirect away
  if (user) {
    navigate("/dashboard", { replace: true });
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result =
        mode === "signup"
          ? await signUp({ email, password, fullName })
          : await signIn({ email, password });

      if (result.error) {
        setError(result.error.message || "Something went wrong.");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
      </nav>

      <div className="gb-main gb-auth-main">
        <div className="gb-card gb-auth-card">
          <div className="gb-auth-tabs" role="tablist">
            <button
              role="tab"
              aria-selected={mode === "login"}
              className={`gb-auth-tab ${mode === "login" ? "gb-auth-tab--active" : ""}`}
              onClick={() => { setMode("login"); setError(null); }}
            >
              Log in
            </button>
            <button
              role="tab"
              aria-selected={mode === "signup"}
              className={`gb-auth-tab ${mode === "signup" ? "gb-auth-tab--active" : ""}`}
              onClick={() => { setMode("signup"); setError(null); }}
            >
              Sign up
            </button>
          </div>

          <div className="gb-auth-body">
            <p className="gb-hero-kicker" style={{ marginBottom: "1rem" }}>
              {mode === "signup" ? "Create your account" : "Welcome back"}
            </p>

            {/* LinkedIn OAuth — wired in Milestone 5 */}
            <button type="button" className="gb-btn gb-btn-linkedin" disabled>
              <LinkedInIcon />
              Continue with LinkedIn
              <span className="gb-badge">Coming soon</span>
            </button>

            <div className="gb-auth-divider">
              <span>or use email</span>
            </div>

            <form onSubmit={handleSubmit} className="gb-auth-form">
              {mode === "signup" && (
                <label className="gb-field">
                  <span>Full name</span>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    autoComplete="name"
                    placeholder="Priya Sharma"
                  />
                </label>
              )}

              <label className="gb-field">
                <span>Email</span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  placeholder="priya@example.com"
                />
              </label>

              <label className="gb-field">
                <span>Password</span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete={mode === "signup" ? "new-password" : "current-password"}
                  placeholder="••••••••"
                  minLength={8}
                />
              </label>

              {error && <p className="gb-auth-error" role="alert">{error}</p>}

              <button type="submit" className="gb-btn gb-btn-primary gb-btn-full" disabled={loading}>
                {loading ? "Please wait…" : mode === "signup" ? "Create account" : "Log in"}
              </button>
            </form>

            <p className="gb-auth-footer-note">
              {mode === "login" ? (
                <>No account? <button className="gb-link-btn" onClick={() => setMode("signup")}>Sign up free</button></>
              ) : (
                <>Already have an account? <button className="gb-link-btn" onClick={() => setMode("login")}>Log in</button></>
              )}
            </p>
          </div>
        </div>

        <p className="gb-auth-skip">
          <Link to="/">Continue without an account →</Link>
        </p>
      </div>
    </div>
  );
}

function LinkedInIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  );
}
