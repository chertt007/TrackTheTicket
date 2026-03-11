from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ServiceSettings:
    service_name: str
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "dev"
    log_level: str = "INFO"
    app_version: str = "0.1.0"

    def __post_init__(self) -> None:
        if not (1 <= self.port <= 65535):
            raise ValueError("PORT must be between 1 and 65535")

    @classmethod
    def from_env(
        cls,
        service_name: str,
        env: Mapping[str, str] | None = None,
    ) -> "ServiceSettings":
        source = env or os.environ
        raw_port = source.get("PORT", "8000")
        try:
            port = int(raw_port)
        except ValueError as exc:
            raise ValueError("PORT must be an integer") from exc

        return cls(
            service_name=service_name,
            host=source.get("HOST", "0.0.0.0"),
            port=port,
            environment=source.get("APP_ENV", "dev"),
            log_level=source.get("LOG_LEVEL", "INFO").upper(),
            app_version=source.get("APP_VERSION", "0.1.0"),
        )

