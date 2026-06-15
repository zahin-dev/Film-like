"""
Application configuration.

Centralises all environment variables using Pydantic Settings.
All settings are loaded once at startup and accessible via the settings instance.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str
    SECRET_KEY: str
    TMDB_READ_ACCESS_TOKEN: str


settings = Settings()
