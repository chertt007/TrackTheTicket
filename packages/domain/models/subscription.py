"""Domain entity models used across the system."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class Subscription:
    id: str
    source_url: str
    origin: str
    destination: str
    departure_at: datetime
    return_at: datetime | None
    airline_code: str
    airline_name: str
    airline_domain: str
    flight_number: str | None
    baggage_mode: str
    reports_per_day: int
    fast_source_type: str
    direct_strategy_id: str | None
    status: str

    def to_dict(self) -> dict[str, str | int | None]:
        """Serialize object data into a dictionary payload."""
        payload = asdict(self)
        payload["departure_at"] = self.departure_at.isoformat()
        payload["return_at"] = self.return_at.isoformat() if self.return_at else None
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str | int | None]) -> "Subscription":
        """Build an object instance from a dictionary payload."""
        return cls(
            id=str(data["id"]),
            source_url=str(data["source_url"]),
            origin=str(data["origin"]),
            destination=str(data["destination"]),
            departure_at=datetime.fromisoformat(str(data["departure_at"])),
            return_at=datetime.fromisoformat(str(data["return_at"])) if data["return_at"] else None,
            airline_code=str(data["airline_code"]),
            airline_name=str(data["airline_name"]),
            airline_domain=str(data["airline_domain"]),
            flight_number=str(data["flight_number"]) if data["flight_number"] else None,
            baggage_mode=str(data["baggage_mode"]),
            reports_per_day=int(data["reports_per_day"]),
            fast_source_type=str(data["fast_source_type"]),
            direct_strategy_id=str(data["direct_strategy_id"]) if data["direct_strategy_id"] else None,
            status=str(data["status"]),
        )

