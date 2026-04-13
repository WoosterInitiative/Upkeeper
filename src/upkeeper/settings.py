"""
Centralized application settings.

Uses pydantic-settings to load environment variables and .env file.
Controls things like DEBUG mode and logging defaults.

Additional settings can be added as needed.
"""

import logging
from pathlib import Path
from typing import Annotated

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

type DBPath = Path | AnyUrl

VERSION = "0.1.0"


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="UPKEEPER_",
        extra="ignore",
    )

    app_name: str = "Upkeeper"
    db_path: DBPath = Path("data/db.sqlite3")

    debug: bool = False
    # Set via UPKEEPER_LOG_LEVEL env var: TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_level: str | None = None

    max_slug_counter: Annotated[
        int, Field(description="Maximum number to append to slug for uniqueness before giving up")
    ] = 1000

    @property
    def default_log_level(self) -> int:
        if self.debug:
            return logging.DEBUG
        return logging.INFO

    @property
    def database_url(self) -> AnyUrl:
        if isinstance(self.db_path, AnyUrl):
            return self.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return AnyUrl(f"sqlite:///{self.db_path.resolve()}")


settings = Settings()
