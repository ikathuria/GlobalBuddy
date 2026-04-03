from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve .env next to the backend package (works even if cwd is repo root).
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_REPO_DIR = _BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings — Neo4j required; at least one AI backend required for plan/bridge."""

    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    neo4j_uri: str = Field(..., min_length=1, description="Neo4j Aura bolt URI")
    neo4j_user: str = Field(..., min_length=1)
    neo4j_password: str = Field(..., min_length=1)

    # AI — Gemini is the default implementation; RocketRide SDK / HTTP / Anthropic are alternates.
    ai_provider: str = Field(
        default="auto",
        description=(
            "auto | gemini | rocketride_sdk | rocketride_http | anthropic "
            "— auto prefers Gemini when GEMINI_API_KEY is set"
        ),
    )
    gemini_api_key: str = Field(default="", description="Google AI Studio / Vertex-compatible Gemini API key")
    gemini_model: str = Field(default="gemini-2.0-flash", description="Gemini model id for generateContent")

    anthropic_api_key: str = Field(default="", description="Optional Anthropic fallback via httpx")

    rocketride_uri: str = Field(default="", description="RocketRide DAP base URI (e.g. https://cloud.rocketride.ai)")
    rocketride_apikey: str = Field(default="", description="RocketRide API key for SDK/HTTP")
    rocketride_gemini_key: str = Field(
        default="",
        description="Gemini API key injected into ROCKETRIDE_GEMINI_KEY for default RocketRide pipelines",
    )
    rocketride_plan_pipeline: str = Field(
        default=str((_REPO_DIR / "pipelines" / "globaldost.plan.pipe").resolve()),
        description="Absolute or relative path to the RocketRide pipeline for /v1/plan/generate",
    )
    rocketride_bridge_pipeline: str = Field(
        default=str((_REPO_DIR / "pipelines" / "globaldost.bridge.pipe").resolve()),
        description="Absolute or relative path to the RocketRide pipeline for /v1/bridge/explain",
    )
    rocketride_http_completion_url: str = Field(
        default="",
        description="Legacy full HTTPS URL for RocketRide HTTP JSON inference",
    )

    cors_origins: str = Field(default="http://localhost:5173")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return ",".join(str(item).strip() for item in value if str(item).strip())
        return str(value)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def require_llm_backend(self) -> "Settings":
        has_gemini = bool(self.gemini_api_key.strip())
        has_rr_sdk = bool(self.rocketride_uri.strip() and self.rocketride_apikey.strip())
        has_rr_http = bool(self.rocketride_http_completion_url.strip() and self.rocketride_apikey.strip())
        has_anthropic = bool(self.anthropic_api_key.strip())
        if not (has_gemini or has_rr_sdk or has_rr_http or has_anthropic):
            raise ValueError(
                "Set GEMINI_API_KEY (recommended), or ROCKETRIDE_URI with ROCKETRIDE_APIKEY, "
                "or ROCKETRIDE_HTTP_COMPLETION_URL with ROCKETRIDE_APIKEY, or ANTHROPIC_API_KEY "
                "for plan/bridge endpoints."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


class Neo4jOnlySettings(BaseSettings):
    """Neo4j only — used by the seed script so LLM keys are not required."""

    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    neo4j_uri: str = Field(..., min_length=1)
    neo4j_user: str = Field(..., min_length=1)
    neo4j_password: str = Field(..., min_length=1)


def get_neo4j_settings() -> Neo4jOnlySettings:
    return Neo4jOnlySettings()
