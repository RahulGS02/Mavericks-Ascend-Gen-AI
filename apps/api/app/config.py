from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: Optional[str] = None

    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # AI Configuration
    AI_ENABLED: bool = False  # Disabled by default for production safety
    AI_PROVIDER: str = "auggie"  # Options: "auggie", "anthropic", "claude_cli"

    # Auggie SDK (CURRENTLY ACTIVE - WORKING)
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "claude-sonnet-4.5"

    # Claude CLI (for local testing - not working)
    CLAUDE_CLI_MODE: str = "headless"
    CLAUDE_CODE_OAUTH_TOKEN: Optional[str] = None

    # Anthropic Claude API (for future production)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 4000
    ANTHROPIC_TEMPERATURE: float = 0.7

    # AI Usage Limits
    AI_DAILY_REQUEST_LIMIT: int = 1000
    AI_RATE_LIMIT_PER_MINUTE: int = 60

    # AI Feature Flags
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
    MAX_RESUME_SIZE: int = 5242880  # 5MB for resumes
    MAX_EXCEL_SIZE: int = 10485760  # 10MB for Excel files

    # Allowed file types
    ALLOWED_RESUME_TYPES: str = "application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ALLOWED_EXCEL_TYPES: str = "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv"

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
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def ai_features_enabled(self) -> bool:
        """Check if AI features should be enabled"""
        # In production, AI must be explicitly enabled
        if self.is_production and not self.AI_ENABLED:
            return False

        # Check based on provider
        if self.AI_PROVIDER == "auggie":
            return self.AI_ENABLED and self.AI_API_KEY is not None
        elif self.AI_PROVIDER == "anthropic":
            return self.AI_ENABLED and self.ANTHROPIC_API_KEY is not None
        elif self.AI_PROVIDER == "claude_cli":
            # Claude CLI just needs to be enabled (will use login or token)
            return self.AI_ENABLED
        else:
            return False

    class ConfigDict:
        env_file = ".env"
        case_sensitive = True

    def model_post_init(self, __context) -> None:
        """Validate required fields in non-test environments"""
        is_testing = os.getenv("TESTING", "").lower() in ("true", "1", "yes")

        if not is_testing:
            # In production/development, these fields are required
            if not self.DATABASE_URL:
                raise ValueError("DATABASE_URL is required in non-test environments")
            if not self.SUPABASE_URL:
                raise ValueError("SUPABASE_URL is required in non-test environments")
            if not self.SUPABASE_SERVICE_KEY:
                raise ValueError("SUPABASE_SERVICE_KEY is required in non-test environments")
            if not self.JWT_SECRET:
                raise ValueError("JWT_SECRET is required in non-test environments")


settings = Settings()
