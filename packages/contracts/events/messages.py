from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class FastCheckCompletedEvent:
    check_job_id: str
    subscription_id: str
    fast_source_status: str
    fast_source_price: float | None
    fast_source_currency: str | None
    occurred_at: datetime

    def to_dict(self) -> dict[str, str | float | None]:
        payload = asdict(self)
        payload["occurred_at"] = self.occurred_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str | float | None]) -> "FastCheckCompletedEvent":
        return cls(
            check_job_id=str(data["check_job_id"]),
            subscription_id=str(data["subscription_id"]),
            fast_source_status=str(data["fast_source_status"]),
            fast_source_price=float(data["fast_source_price"]) if data["fast_source_price"] else None,
            fast_source_currency=(
                str(data["fast_source_currency"]) if data["fast_source_currency"] else None
            ),
            occurred_at=datetime.fromisoformat(str(data["occurred_at"])),
        )


@dataclass(frozen=True)
class DirectCheckCompletedEvent:
    check_job_id: str
    subscription_id: str
    direct_status: str
    direct_price: float | None
    direct_currency: str | None
    direct_screenshot_url: str | None
    is_match_confirmed: bool
    occurred_at: datetime

    def to_dict(self) -> dict[str, str | float | bool | None]:
        payload = asdict(self)
        payload["occurred_at"] = self.occurred_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str | float | bool | None]) -> "DirectCheckCompletedEvent":
        return cls(
            check_job_id=str(data["check_job_id"]),
            subscription_id=str(data["subscription_id"]),
            direct_status=str(data["direct_status"]),
            direct_price=float(data["direct_price"]) if data["direct_price"] else None,
            direct_currency=str(data["direct_currency"]) if data["direct_currency"] else None,
            direct_screenshot_url=(
                str(data["direct_screenshot_url"]) if data["direct_screenshot_url"] else None
            ),
            is_match_confirmed=bool(data["is_match_confirmed"]),
            occurred_at=datetime.fromisoformat(str(data["occurred_at"])),
        )


@dataclass(frozen=True)
class ReconcileAndNotifyRequestedEvent:
    check_job_id: str
    subscription_id: str
    triggered_at: datetime

    def to_dict(self) -> dict[str, str]:
        payload = asdict(self)
        payload["triggered_at"] = self.triggered_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "ReconcileAndNotifyRequestedEvent":
        return cls(
            check_job_id=str(data["check_job_id"]),
            subscription_id=str(data["subscription_id"]),
            triggered_at=datetime.fromisoformat(str(data["triggered_at"])),
        )

