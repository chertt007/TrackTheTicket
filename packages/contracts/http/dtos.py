"""Contract models shared between services for HTTP and events."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateSubscriptionRequest:
    source_url: str
    baggage_mode: str
    reports_per_day: int

    def to_dict(self) -> dict[str, str | int]:
        """Serialize object data into a dictionary payload."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str | int]) -> "CreateSubscriptionRequest":
        """Build an object instance from a dictionary payload."""
        return cls(
            source_url=str(data["source_url"]),
            baggage_mode=str(data["baggage_mode"]),
            reports_per_day=int(data["reports_per_day"]),
        )


@dataclass(frozen=True)
class CreateSubscriptionResponse:
    subscription_id: str
    status: str
    created_at: datetime

    def to_dict(self) -> dict[str, str]:
        """Serialize object data into a dictionary payload."""
        payload = asdict(self)
        payload["created_at"] = self.created_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "CreateSubscriptionResponse":
        """Build an object instance from a dictionary payload."""
        return cls(
            subscription_id=str(data["subscription_id"]),
            status=str(data["status"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )


@dataclass(frozen=True)
class CheckResultResponse:
    subscription_id: str
    fast_source_price: float | None
    direct_price: float | None
    better_source: str | None
    final_summary: str
    checked_at: datetime

    def to_dict(self) -> dict[str, str | float | None]:
        """Serialize object data into a dictionary payload."""
        payload = asdict(self)
        payload["checked_at"] = self.checked_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str | float | None]) -> "CheckResultResponse":
        """Build an object instance from a dictionary payload."""
        return cls(
            subscription_id=str(data["subscription_id"]),
            fast_source_price=float(data["fast_source_price"]) if data["fast_source_price"] else None,
            direct_price=float(data["direct_price"]) if data["direct_price"] else None,
            better_source=str(data["better_source"]) if data["better_source"] else None,
            final_summary=str(data["final_summary"]),
            checked_at=datetime.fromisoformat(str(data["checked_at"])),
        )

