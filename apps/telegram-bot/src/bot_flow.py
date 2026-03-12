"""Conversation state machine for Telegram subscription commands."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class SubscriptionClientProtocol(Protocol):
    def create_subscription(
        self, source_url: str, baggage_mode: str, reports_per_day: int, chat_id: str
    ) -> dict:
        """Create subscription."""
        ...

    def pause_subscription(self, subscription_id: str) -> dict:
        """Pause subscription."""
        ...

    def resume_subscription(self, subscription_id: str) -> dict:
        """Resume subscription."""
        ...

    def delete_subscription(self, subscription_id: str) -> dict:
        """Delete subscription."""
        ...


@dataclass
class DraftSubscription:
    source_url: str | None = None
    baggage_mode: str | None = None


class TelegramConversationManager:
    def __init__(self, subscription_client: SubscriptionClientProtocol) -> None:
        """Initialize object state and dependencies."""
        self.subscription_client = subscription_client
        self.sessions: dict[str, dict[str, object]] = {}

    def handle_message(self, chat_id: str, text: str) -> dict[str, str]:
        """Handle message."""
        text = text.strip()
        if not text:
            return {"reply": "Пустое сообщение. Отправьте команду /new для создания подписки."}

        if text.startswith("/pause "):
            subscription_id = text.split(maxsplit=1)[1].strip()
            self.subscription_client.pause_subscription(subscription_id)
            return {"reply": f"Подписка {subscription_id} поставлена на паузу."}

        if text.startswith("/resume "):
            subscription_id = text.split(maxsplit=1)[1].strip()
            self.subscription_client.resume_subscription(subscription_id)
            return {"reply": f"Подписка {subscription_id} возобновлена."}

        if text.startswith("/delete "):
            subscription_id = text.split(maxsplit=1)[1].strip()
            self.subscription_client.delete_subscription(subscription_id)
            return {"reply": f"Подписка {subscription_id} удалена."}

        session = self.sessions.get(chat_id)
        if text in {"/start", "/new"}:
            self.sessions[chat_id] = {"state": "awaiting_url", "draft": DraftSubscription()}
            return {"reply": "Отправьте ссылку на билет или страницу поиска."}

        if session is None:
            return {"reply": "Для начала отправьте /new. Для управления: /pause <id>, /resume <id>, /delete <id>."}

        state = str(session["state"])
        draft = session["draft"]
        if not isinstance(draft, DraftSubscription):
            self.sessions.pop(chat_id, None)
            return {"reply": "Сессия сброшена. Отправьте /new и начните снова."}

        if state == "awaiting_url":
            draft.source_url = text
            session["state"] = "awaiting_baggage"
            return {"reply": "Укажите режим багажа: cabin_only или checked_bag."}

        if state == "awaiting_baggage":
            baggage_mode = text.lower()
            if baggage_mode not in {"cabin_only", "checked_bag"}:
                return {"reply": "Некорректный режим багажа. Допустимо: cabin_only или checked_bag."}
            draft.baggage_mode = baggage_mode
            session["state"] = "awaiting_reports"
            return {"reply": "Укажите частоту отчетов (число отчетов в день, от 1 до 24)."}

        if state == "awaiting_reports":
            if not text.isdigit():
                return {"reply": "Частота должна быть числом от 1 до 24."}
            reports_per_day = int(text)
            if reports_per_day < 1 or reports_per_day > 24:
                return {"reply": "Частота должна быть в диапазоне от 1 до 24."}
            if draft.source_url is None or draft.baggage_mode is None:
                self.sessions.pop(chat_id, None)
                return {"reply": "Сессия повреждена. Отправьте /new и начните снова."}

            created = self.subscription_client.create_subscription(
                source_url=draft.source_url,
                baggage_mode=draft.baggage_mode,
                reports_per_day=reports_per_day,
                chat_id=chat_id,
            )
            self.sessions.pop(chat_id, None)
            return {
                "reply": (
                    f"Подписка создана: {created['subscription_id']}. "
                    f"Статус: {created['status']}. Отчетов в день: {reports_per_day}."
                )
            }

        self.sessions.pop(chat_id, None)
        return {"reply": "Неизвестное состояние сессии. Отправьте /new и начните снова."}

