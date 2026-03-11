from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class CheckResult:
    id: str
    check_job_id: str
    fast_source_price: float | None
    fast_source_currency: str | None
    fast_source_status: str
    direct_price: float | None
    direct_currency: str | None
    direct_status: str
    direct_screenshot_url: str | None
    is_match_confirmed: bool
    better_source: str | None
    final_summary: str
    checked_at: datetime

    def to_dict(self) -> dict[str, str | float | bool | None]:
        payload = asdict(self)
        payload["checked_at"] = self.checked_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str | float | bool | None]) -> "CheckResult":
        return cls(
            id=str(data["id"]),
            check_job_id=str(data["check_job_id"]),
            fast_source_price=float(data["fast_source_price"]) if data["fast_source_price"] else None,
            fast_source_currency=(
                str(data["fast_source_currency"]) if data["fast_source_currency"] else None
            ),
            fast_source_status=str(data["fast_source_status"]),
            direct_price=float(data["direct_price"]) if data["direct_price"] else None,
            direct_currency=str(data["direct_currency"]) if data["direct_currency"] else None,
            direct_status=str(data["direct_status"]),
            direct_screenshot_url=(
                str(data["direct_screenshot_url"]) if data["direct_screenshot_url"] else None
            ),
            is_match_confirmed=bool(data["is_match_confirmed"]),
            better_source=str(data["better_source"]) if data["better_source"] else None,
            final_summary=str(data["final_summary"]),
            checked_at=datetime.fromisoformat(str(data["checked_at"])),
        )

