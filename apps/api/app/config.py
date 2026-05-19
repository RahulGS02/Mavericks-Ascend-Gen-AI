from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str

    # AI Configuration
    AI_ENABLED: bool = False  # Disabled by default for production safety
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "claude-sonnet-4.5"
    AI_MAX_TOKENS: int = 4000
    AI_TEMPERATURE: float = 0.7

    # AI Usage Limits
    AI_DAILY_REQUEST_LIMIT: int = 1000
    AI_RATE_LIMIT_PER_MINUTE: int = 60

    # AI Feature Flags
    AI_RESUME_PARSING_ENABLED: bool = True
    AI_SKILL_EXTRACTION_ENABLED: bool = True
    AI_PERFORMANCE_INSIGHTS_ENABLED: bool = True

    # JWT
    JWT_SECRET: str
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
        return self.AI_ENABLED and self.AI_API_KEY is not None

    class ConfigDict:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
