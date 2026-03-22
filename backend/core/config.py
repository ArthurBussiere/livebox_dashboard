from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # HTTP client timeout in seconds (per request)
    request_timeout: float = 10.0

    # Session TTL in seconds (default 24h)
    session_ttl: int = 86400

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LIVEBOX_",
        extra="ignore",
        # Env vars: LIVEBOX_REQUEST_TIMEOUT, LIVEBOX_SESSION_TTL
    )


settings = Settings()
