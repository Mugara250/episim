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

    jwt_secret: str = "change-me"
    jwt_lifetime_seconds: int = 3600

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@episim.local"


settings = Settings()
