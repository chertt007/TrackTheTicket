from __future__ import annotations

import socket
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBSCRIPTION_SRC = ROOT / "services" / "subscription-service" / "src"
TELEGRAM_SRC = ROOT / "apps" / "telegram-bot" / "src"

import sys

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
if str(SUBSCRIPTION_SRC) not in sys.path:
    sys.path.append(str(SUBSCRIPTION_SRC))
if str(TELEGRAM_SRC) not in sys.path:
    sys.path.append(str(TELEGRAM_SRC))

from bot_flow import TelegramConversationManager
from packages.shared.config.settings import ServiceSettings
from repository import SubscriptionRepository
from service import SubscriptionService
from subscription_client import SubscriptionApiClient
from api import create_server


class TelegramSubscriptionFlowTests(unittest.TestCase):
    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        db_path = str(Path(self.tmp_dir.name) / "subscriptions.db")
        repo = SubscriptionRepository(db_path=db_path)
        service = SubscriptionService(repo)
        self.port = self._find_free_port()
        settings = ServiceSettings(
            service_name="subscription-service-test",
            host="127.0.0.1",
            port=self.port,
            environment="test",
            app_version="0.0.0",
        )
        self.server = create_server(settings, service)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        self.client = SubscriptionApiClient(base_url=f"http://127.0.0.1:{self.port}")
        self.manager = TelegramConversationManager(self.client)

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp_dir.cleanup()

    def test_create_subscription_through_telegram_dialog(self) -> None:
        chat_id = "tg-123"

        r1 = self.manager.handle_message(chat_id, "/new")
        self.assertIn("Отправьте ссылку", r1["reply"])

        r2 = self.manager.handle_message(chat_id, "https://example.com/flight-offer")
        self.assertIn("режим багажа", r2["reply"])

        r3 = self.manager.handle_message(chat_id, "checked_bag")
        self.assertIn("частоту отчетов", r3["reply"])

        r4 = self.manager.handle_message(chat_id, "4")
        self.assertIn("Подписка создана:", r4["reply"])

        subscription_id = r4["reply"].split("Подписка создана: ")[1].split(".")[0]
        fetched = self.client.get_subscription(subscription_id)
        subscription = fetched["subscription"]
        self.assertEqual(subscription["source_url"], "https://example.com/flight-offer")
        self.assertEqual(subscription["baggage_mode"], "checked_bag")
        self.assertEqual(subscription["reports_per_day"], 4)
        self.assertEqual(subscription["chat_id"], chat_id)
        self.assertEqual(subscription["status"], "active")

    def test_pause_resume_delete_commands(self) -> None:
        created = self.client.create_subscription(
            source_url="https://example.com/f",
            baggage_mode="cabin_only",
            reports_per_day=2,
            chat_id="tg-777",
        )
        subscription_id = created["subscription_id"]

        pause_reply = self.manager.handle_message("tg-777", f"/pause {subscription_id}")
        self.assertIn("поставлена на паузу", pause_reply["reply"])

        resume_reply = self.manager.handle_message("tg-777", f"/resume {subscription_id}")
        self.assertIn("возобновлена", resume_reply["reply"])

        delete_reply = self.manager.handle_message("tg-777", f"/delete {subscription_id}")
        self.assertIn("удалена", delete_reply["reply"])


if __name__ == "__main__":
    unittest.main()

