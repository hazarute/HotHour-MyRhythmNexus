from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HotHour"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:5173", "http://localhost:8000"]
    FRONTEND_URL: str = "http://localhost:5173"  # Frontend URL for email links
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str

    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2 # 2 days
    # Refresh tokens lifetime (in days)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 7 days
    SECRET_KEY: str = "change-me-locally" # Bu değer .env'den ezilir
    # Redis (optional) for shared state like token revocation
    REDIS_URL: str | None = None
    # Key prefix used in Redis for revoked tokens
    REDIS_REVOKED_KEY_PREFIX: str = "revoked_refresh:"

    # Email
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_user: str | None = None
    SMTP_PASSWORD: str | None = None
    GMAIL_API_ENABLED: bool = False
    GMAIL_CLIENT_ID: str | None = None
    GMAIL_CLIENT_SECRET: str | None = None
    GMAIL_REFRESH_TOKEN: str | None = None
    GMAIL_SENDER_EMAIL: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: str | None, values: dict[str, any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v
    
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool | str, values: dict[str, any]) -> bool:
        smtp_ready = bool(values.get("SMTP_HOST") and values.get("SMTP_PORT") and values.get("EMAILS_FROM_EMAIL"))
        gmail_ready = bool(
            values.get("GMAIL_API_ENABLED")
            and values.get("GMAIL_CLIENT_ID")
            and values.get("GMAIL_CLIENT_SECRET")
            and values.get("GMAIL_REFRESH_TOKEN")
            and (values.get("GMAIL_SENDER_EMAIL") or values.get("EMAILS_FROM_EMAIL"))
        )
        return smtp_ready or gmail_ready

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
