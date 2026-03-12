"""Business logic layer for subscription lifecycle operations."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from repository import SubscriptionRepository


class SubscriptionService:
    def __init__(self, repository: SubscriptionRepository) -> None:
        """Initialize object state and dependencies."""
        self.repository = repository

    def create_subscription(
        self,
        source_url: str,
        baggage_mode: str,
        reports_per_day: int,
        chat_id: str | None = None,
    ) -> dict[str, str | int | None]:
        """Create subscription."""
        if not source_url.strip():
            raise ValueError("source_url is required")
        if not baggage_mode.strip():
            raise ValueError("baggage_mode is required")
        if reports_per_day < 1:
            raise ValueError("reports_per_day must be >= 1")

        now = datetime.now(timezone.utc).isoformat()
        subscription_id = str(uuid4())
        payload = {
            "id": subscription_id,
            "chat_id": chat_id,
            "source_url": source_url.strip(),
            "baggage_mode": baggage_mode.strip(),
            "reports_per_day": reports_per_day,
            "status": "active",
            "created_at": now,
        }
        self.repository.create(payload)
        return payload

    def get_subscription(self, subscription_id: str) -> dict[str, str | int | None] | None:
        """Fetch subscription."""
        return self.repository.get(subscription_id)

    def pause_subscription(self, subscription_id: str) -> bool:
        """Pause subscription."""
        return self.repository.update_status(subscription_id, "paused")

    def resume_subscription(self, subscription_id: str) -> bool:
        """Resume subscription."""
        return self.repository.update_status(subscription_id, "active")

    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete subscription."""
        return self.repository.delete(subscription_id)
