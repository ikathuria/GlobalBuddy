import { useMemo, useState } from "react";
import client from "../api/client.js";

const defaultProfile = {
  full_name: "",
  email: "",
  country_of_origin: "India",
  home_city: "Bengaluru",
  target_university: "Illinois Institute of Technology",
  target_city: "Chicago",
  needs: "banking, housing, community",
  interests: "south indian food, hackathons, tech meetups, luma events",
  cultural_background: "South Indian",
  religion_or_observance: "Hindu",
  diet: "vegetarian",
  linkedin_url: "",
  instagram_url: "",
  other_social_url: "",
  new_to_us: true,
};

const STEPS = [
  {
    id: "personal",
    title: "Personal Info",
    helper: "We only need basics to personalize your support map.",
    required: ["full_name", "email"],
  },
  {
    id: "origin",
    title: "Origin and Context",
    helper: "This helps us surface culturally relevant people and places.",
    required: ["country_of_origin", "home_city"],
  },
  {
    id: "destination",
    title: "Destination",
    helper: "Tell us where you are headed so your first month plan is local and practical.",
    required: ["target_university", "target_city"],
  },
];

function parseCommaList(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function getErrorText(error) {
  if (!error) return null;
  return typeof error === "string" ? error : JSON.stringify(error);
}

function ProgressBar({ step }) {
  const progress = ((step + 1) / STEPS.length) * 100;
  return (
    <div className="gb-stepper-progress" aria-label="Profile setup progress">
      <div className="gb-stepper-progress__meta">
        <strong>
          Step {step + 1} of {STEPS.length}
        </strong>
        <span>{STEPS[step].title}</span>
      </div>
      <div className="gb-stepper-progress__track" role="presentation">
        <div className="gb-stepper-progress__bar" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}

export default function ProfileForm({ onMatch }) {
  const [form, setForm] = useState(defaultProfile);
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const nextStepDisabled = useMemo(() => {
    const requiredFields = STEPS[step].required || [];
    return requiredFields.some((field) => !String(form[field] || "").trim());
  }, [form, step]);

  const update = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const useSmartStarter = () => {
    setForm((prev) => ({
      ...defaultProfile,
      full_name: prev.full_name,
      email: prev.email,
      target_university: prev.target_university || defaultProfile.target_university,
      target_city: prev.target_city || defaultProfile.target_city,
    }));
  };

  const goNext = () => {
    if (nextStepDisabled) {
      setError("Please complete the required fields in this step.");
      return;
    }
    setError(null);
    setStep((prev) => Math.min(prev + 1, STEPS.length - 1));
  };

  const goBack = () => {
    setError(null);
    setStep((prev) => Math.max(prev - 1, 0));
  };

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        country_of_origin: form.country_of_origin.trim(),
        home_city: form.home_city.trim(),
        target_university: form.target_university.trim(),
        target_city: form.target_city.trim(),
        needs: parseCommaList(form.needs),
        interests: parseCommaList(form.interests),
        new_to_us: Boolean(form.new_to_us),
        cultural_background: form.cultural_background.trim(),
        religion_or_observance: form.religion_or_observance.trim(),
        diet: form.diet.trim(),
        linkedin_url: form.linkedin_url.trim(),
        instagram_url: form.instagram_url.trim(),
        other_social_url: form.other_social_url.trim(),
      };

      const response = await client.post("/v1/profile/match", payload);
      onMatch(response.data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="gb-stepper" aria-label="Profile setup wizard">
      <div className="gb-stepper-head">
        <h2>Step 1: Profile setup</h2>
        <p>
          No paperwork needed. We use this once to personalize your plan, local graph, and first introductions.
        </p>
        <button type="button" className="gb-btn gb-btn-ghost" onClick={useSmartStarter}>
          Use smart starter defaults
        </button>
      </div>

      <ProgressBar step={step} />

      <ol className="gb-stepper-tabs" aria-label="Profile steps">
        {STEPS.map((item, index) => {
          const state = index < step ? "done" : index === step ? "active" : "pending";
          return (
            <li key={item.id} className={`gb-stepper-tab gb-stepper-tab--${state}`}>
              <button type="button" onClick={() => setStep(index)} disabled={loading}>
                <span>{item.title}</span>
              </button>
            </li>
          );
        })}
      </ol>

      <form onSubmit={submit} className="gb-stepper-form">
        <div className="gb-stepper-panel">
          <h3>{STEPS[step].title}</h3>
          <p>{STEPS[step].helper}</p>

          {step === 0 && (
            <div className="gb-form-grid">
              <label className="gb-field">
                <span>Full name *</span>
                <input
                  value={form.full_name}
                  onChange={(event) => update("full_name", event.target.value)}
                  autoComplete="name"
                  placeholder="Your full name"
                  required
                />
                <small>We use this for mentor introductions.</small>
              </label>

              <label className="gb-field">
                <span>Email address *</span>
                <input
                  type="email"
                  value={form.email}
                  onChange={(event) => update("email", event.target.value)}
                  autoComplete="email"
                  placeholder="name@example.com"
                  required
                />
                <small>Only used for connection follow-ups.</small>
              </label>

              <fieldset className="gb-field gb-field--full gb-radio-fieldset">
                <legend>Are you new to the US?</legend>
                <div className="gb-radio-row" role="radiogroup" aria-label="New to the US">
                  <label>
                    <input
                      type="radio"
                      name="new_to_us"
                      checked={form.new_to_us === true}
                      onChange={() => update("new_to_us", true)}
                    />
                    Yes, this is my first time living in the US.
                  </label>
                  <label>
                    <input
                      type="radio"
                      name="new_to_us"
                      checked={form.new_to_us === false}
                      onChange={() => update("new_to_us", false)}
                    />
                    No, I have lived in the US before.
                  </label>
                </div>
              </fieldset>
            </div>
          )}

          {step === 1 && (
            <div className="gb-form-grid">
              <label className="gb-field">
                <span>Country of origin *</span>
                <input
                  value={form.country_of_origin}
                  onChange={(event) => update("country_of_origin", event.target.value)}
                  autoComplete="country-name"
                  placeholder="India"
                  required
                />
                <small>Used for cultural context and language cues.</small>
              </label>

              <label className="gb-field">
                <span>Home city *</span>
                <input
                  value={form.home_city}
                  onChange={(event) => update("home_city", event.target.value)}
                  placeholder="Bengaluru"
                  required
                />
                <small>Helps with shared-background matching.</small>
              </label>

              <label className="gb-field gb-field--full">
                <span>Needs (comma-separated)</span>
                <input
                  value={form.needs}
                  onChange={(event) => update("needs", event.target.value)}
                  placeholder="banking, housing, community"
                />
                <small>List immediate priorities for your first month.</small>
              </label>

              <label className="gb-field gb-field--full">
                <span>Interests (comma-separated)</span>
                <input
                  value={form.interests}
                  onChange={(event) => update("interests", event.target.value)}
                  placeholder="food, campus events, hackathons"
                />
                <small>Used to suggest places and events you may enjoy.</small>
              </label>

              <label className="gb-field">
                <span>Cultural background</span>
                <input
                  value={form.cultural_background}
                  onChange={(event) => update("cultural_background", event.target.value)}
                  placeholder="South Indian"
                />
              </label>

              <label className="gb-field">
                <span>Religion or observance</span>
                <input
                  value={form.religion_or_observance}
                  onChange={(event) => update("religion_or_observance", event.target.value)}
                  placeholder="Hindu"
                />
              </label>

              <label className="gb-field gb-field--full">
                <span>Diet preference</span>
                <input
                  value={form.diet}
                  onChange={(event) => update("diet", event.target.value)}
                  placeholder="vegetarian, halal"
                />
              </label>
            </div>
          )}

          {step === 2 && (
            <div className="gb-form-grid">
              <label className="gb-field gb-field--full">
                <span>Target university *</span>
                <input
                  value={form.target_university}
                  onChange={(event) => update("target_university", event.target.value)}
                  placeholder="Illinois Institute of Technology"
                  required
                />
                <small>This anchors mentor/peer and nearby support matching.</small>
              </label>

              <label className="gb-field">
                <span>Target city (US) *</span>
                <input
                  value={form.target_city}
                  onChange={(event) => update("target_city", event.target.value)}
                  placeholder="Chicago"
                  required
                />
                <small>Used for local resources and event recommendations.</small>
              </label>

              <label className="gb-field">
                <span>LinkedIn URL</span>
                <input
                  value={form.linkedin_url}
                  onChange={(event) => update("linkedin_url", event.target.value)}
                  placeholder="https://www.linkedin.com/in/your-profile"
                />
              </label>

              <label className="gb-field">
                <span>Instagram</span>
                <input
                  value={form.instagram_url}
                  onChange={(event) => update("instagram_url", event.target.value)}
                  placeholder="@yourhandle or profile URL"
                />
              </label>

              <label className="gb-field">
                <span>Other social profile</span>
                <input
                  value={form.other_social_url}
                  onChange={(event) => update("other_social_url", event.target.value)}
                  placeholder="Any additional profile link"
                />
              </label>

              <div className="gb-stepper-summary gb-field--full">
                <strong>Ready check</strong>
                <p>
                  You are headed to <span>{form.target_city || "your target city"}</span> for <span>{form.target_university || "your university"}</span>. Once saved,
                  we will generate your plan and support graph.
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="gb-stepper-actions">
          <button type="button" className="gb-btn gb-btn-secondary" onClick={goBack} disabled={step === 0 || loading}>
            Back
          </button>

          {step < STEPS.length - 1 ? (
            <button type="button" className="gb-btn gb-btn-primary" onClick={goNext} disabled={loading}>
              Next step
            </button>
          ) : (
            <button type="submit" className="gb-btn gb-btn-primary" disabled={loading}>
              {loading ? "Saving your profile..." : "Save profile and continue"}
            </button>
          )}
        </div>
      </form>

      {error && <div className="gb-error">{getErrorText(error)}</div>}
    </section>
  );
}
