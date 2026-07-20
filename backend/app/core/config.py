from functools import lru_cache
from typing import Annotated

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "PulseResolve AI"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite+aiosqlite:///./pulseresolve.db"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    ai_provider: str = "local"
    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "CHATBOT_API_BASE_URL"),
    )
    llm_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_API_KEY", "CHATBOT_API_KEY"),
    )
    llm_model: str = Field(
        default="gpt-4.1-mini",
        validation_alias=AliasChoices("LLM_MODEL", "CHATBOT_MODEL"),
    )
    embedding_model: str = "text-embedding-3-small"
    request_timeout_seconds: float = 30.0
    demo_mode: bool = True

    auto_refund_limit: float = 500.0
    approval_refund_limit: float = 2000.0
    incident_similarity_threshold: float = 0.68
    incident_min_complaints: int = 3
    incident_window_minutes: int = 60

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
