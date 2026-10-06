from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    frontend_url: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://episim:episim@localhost:5432/episim"

    redis_url: str = "redis://localhost:6379/0"

    minio_endpoint: str = "http://localhost:9000"
    minio_root_user: str = "episim_minio"
    minio_root_password: str = "episim_minio_secret"
    minio_bucket: str = "episim"
    minio_region: str = "us-east-1"

    jwt_secret: str = "change-me"
    jwt_lifetime_seconds: int = 3600

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@episim.local"
    # "none" for local catchers like Mailhog, "starttls" for port 587,
    # "ssl" for implicit TLS on port 465.
    smtp_security: Literal["none", "starttls", "ssl"] = "none"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def _check_production_secrets(self) -> "Settings":
        # JWT_SECRET also derives the key that encrypts stored MFA secrets.
        if self.is_production and (self.jwt_secret.startswith("change-me") or len(self.jwt_secret) < 32):
            raise ValueError("JWT_SECRET must be a random string of at least 32 characters in production")
        return self


settings = Settings()
