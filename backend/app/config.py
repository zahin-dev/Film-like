"""Application configuration for the self-hosted Japanese edition."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    DATABASE_URL: str
    SECRET_KEY: str
    RECOMMENDATION_ENGINE: str = "local"
    APP_LOCALE: str = "ja-JP"
    APP_REGION: str = "JP"
    APP_TIMEZONE: str = "Asia/Tokyo"


settings = Settings()
