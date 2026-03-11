from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(frozen=True)
class CheckJob:
    id: str
    subscription_id: str
    fast_check_task_id: str
    direct_airline_check_task_id: str
    reconcile_and_notify_task_id: str
    status: str
    created_at: datetime

    def to_dict(self) -> dict[str, str]:
        payload = asdict(self)
        payload["created_at"] = self.created_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "CheckJob":
        return cls(
            id=str(data["id"]),
            subscription_id=str(data["subscription_id"]),
            fast_check_task_id=str(data["fast_check_task_id"]),
            direct_airline_check_task_id=str(data["direct_airline_check_task_id"]),
            reconcile_and_notify_task_id=str(data["reconcile_and_notify_task_id"]),
            status=str(data["status"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )

