from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # OpenAI
    OPENAI_API_KEY: str
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
