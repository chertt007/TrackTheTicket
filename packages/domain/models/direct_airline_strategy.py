"""Domain entity models used across the system."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class DirectAirlineStrategy:
    id: str
    airline_code: str
    airline_domain: str
    strategy_version: int
    strategy_json: str
    playwright_script: str
    status: str
    success_rate: float
    average_runtime_sec: float
    requires_ai_repair: bool
    last_verified_at: datetime | None

    def to_dict(self) -> dict[str, str | int | float | bool | None]:
        """Serialize object data into a dictionary payload."""
        payload = asdict(self)
        payload["last_verified_at"] = (
            self.last_verified_at.isoformat() if self.last_verified_at else None
        )
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str | int | float | bool | None]) -> "DirectAirlineStrategy":
        """Build an object instance from a dictionary payload."""
        return cls(
            id=str(data["id"]),
            airline_code=str(data["airline_code"]),
            airline_domain=str(data["airline_domain"]),
            strategy_version=int(data["strategy_version"]),
            strategy_json=str(data["strategy_json"]),
            playwright_script=str(data["playwright_script"]),
            status=str(data["status"]),
            success_rate=float(data["success_rate"]),
            average_runtime_sec=float(data["average_runtime_sec"]),
            requires_ai_repair=bool(data["requires_ai_repair"]),
            last_verified_at=(
                datetime.fromisoformat(str(data["last_verified_at"]))
                if data["last_verified_at"]
                else None
            ),
        )

