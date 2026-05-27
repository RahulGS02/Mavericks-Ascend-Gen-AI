from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: Optional[str] = None

    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # =========================================================
    # AI Configuration — Primary Provider: Azure AI Foundry
    # =========================================================
    AI_ENABLED: bool = True        # Azure credentials are baked in — enabled by default
    AI_PROVIDER: str = "azure"     # Options: "azure" | "anthropic" | "claude_cli" | "auggie"

    # ─── Azure AI Foundry (PRIMARY) ──────────────────────────
    # Project name: proj-default-ai  (from original portal URL)
    # The v1 path is OpenAI-compatible; no api-version query param needed.
    AZURE_AI_ENDPOINT: str = ""
    AZURE_AI_API_KEY: str = ""
    AZURE_AI_MODEL: str = "gpt-4.1-mini"      # Deployment name in Azure AI Foundry
    # api-version NOT required -- v1 project endpoint is OpenAI-compatible (confirmed by test)
    # Auth header = api-key (NOT Authorization: Bearer) -- confirmed by test probe
    AZURE_AI_API_VERSION: str = ""   # empty = no api-version query param sent
    AZURE_AI_MAX_TOKENS: int = 4000
    AZURE_AI_TEMPERATURE: float = 0.7

    # ─── Anthropic Claude API (fallback / optional) ──────────
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 4000
    ANTHROPIC_TEMPERATURE: float = 0.7

    # ─── Claude CLI (local dev only) ─────────────────────────
    CLAUDE_CLI_MODE: str = "headless"
    CLAUDE_CODE_OAUTH_TOKEN: Optional[str] = None

    # ─── Auggie SDK (legacy — kept for backward compat) ──────
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "claude-sonnet-4.5"

    # ─── Usage Limits ────────────────────────────────────────
    AI_DAILY_REQUEST_LIMIT: int = 1000
    AI_RATE_LIMIT_PER_MINUTE: int = 60

    # ─── Feature Flags ───────────────────────────────────────
    AI_RESUME_PARSING_ENABLED: bool = True
    AI_SKILL_EXTRACTION_ENABLED: bool = True
    AI_PERFORMANCE_INSIGHTS_ENABLED: bool = True

    # JWT
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"

    # Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    MAX_RESUME_SIZE: int = 5242880   # 5MB for resumes
    MAX_EXCEL_SIZE: int = 10485760   # 10MB for Excel files

    # Allowed file types
    ALLOWED_RESUME_TYPES: str = "application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ALLOWED_EXCEL_TYPES: str = "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv"

    # ─── Derived / alias properties ──────────────────────────

    @property
    def AI_MODEL_DISPLAY(self) -> str:
        """Human-readable model name for API responses"""
        if self.AI_PROVIDER == "azure":
            return f"azure/{self.AZURE_AI_MODEL}"
        elif self.AI_PROVIDER == "anthropic":
            return self.ANTHROPIC_MODEL
        return self.AI_MODEL

    @property
    def AI_MAX_TOKENS(self) -> int:
        """Active provider max tokens — used by /ai/config endpoint"""
        if self.AI_PROVIDER == "azure":
            return self.AZURE_AI_MAX_TOKENS
        return self.ANTHROPIC_MAX_TOKENS

    @property
    def AI_TEMPERATURE(self) -> float:
        """Active provider temperature — used by /ai/config endpoint"""
        if self.AI_PROVIDER == "azure":
            return self.AZURE_AI_TEMPERATURE
        return self.ANTHROPIC_TEMPERATURE

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def allowed_resume_types(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_RESUME_TYPES.split(",")]

    @property
    def allowed_excel_types(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_EXCEL_TYPES.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def ai_features_enabled(self) -> bool:
        """True only when AI is enabled AND the provider credentials are set"""
        if not self.AI_ENABLED:
            return False
        if self.AI_PROVIDER == "azure":
            return bool(self.AZURE_AI_ENDPOINT and self.AZURE_AI_API_KEY)
        elif self.AI_PROVIDER == "anthropic":
            return bool(self.ANTHROPIC_API_KEY)
        elif self.AI_PROVIDER == "claude_cli":
            return True  # Uses existing CLI login session
        else:  # auggie (legacy)
            return bool(self.AI_API_KEY)

    class ConfigDict:
        env_file = ".env"
        case_sensitive = True

    def model_post_init(self, __context) -> None:
        """Validate required fields in non-test environments"""
        is_testing = os.getenv("TESTING", "").lower() in ("true", "1", "yes")

        if not is_testing:
            if not self.DATABASE_URL:
                raise ValueError("DATABASE_URL is required in non-test environments")
            if not self.SUPABASE_URL:
                raise ValueError("SUPABASE_URL is required in non-test environments")
            if not self.SUPABASE_SERVICE_KEY:
                raise ValueError("SUPABASE_SERVICE_KEY is required in non-test environments")
            if not self.JWT_SECRET:
                raise ValueError("JWT_SECRET is required in non-test environments")


settings = Settings()
