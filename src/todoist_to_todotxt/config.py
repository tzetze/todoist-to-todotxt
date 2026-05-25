from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    """Runtime configuration loaded from the environment."""

    todoist_api_token: str
    token_source: str


def load_config() -> Config:
    """Load configuration from environment variables."""
    token = os.environ.get("TODOIST_API_TOKEN", "").strip()
    if not token:
        raise ConfigError("TODOIST_API_TOKEN is required")

    return Config(
        todoist_api_token=token,
        token_source="environment variable TODOIST_API_TOKEN",
    )
