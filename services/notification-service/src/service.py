"""Business logic for notification dispatch operations."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


class NotificationService:
    """Create delivery payloads for downstream user notification channels."""

    def send_notification(self, chat_id: str, message: str, channel: str = "telegram") -> dict[str, str]:
        """Prepare and return notification delivery metadata."""
        if not chat_id.strip():
            raise ValueError("chat_id is required")
        if not message.strip():
            raise ValueError("message is required")

        return {
            "notification_id": str(uuid4()),
            "chat_id": chat_id.strip(),
            "channel": channel.strip() or "telegram",
            "message": message.strip(),
            "status": "sent",
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
