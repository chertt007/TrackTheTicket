from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBSCRIPTION_SRC = ROOT / "services" / "subscription-service" / "src"

import sys

if str(SUBSCRIPTION_SRC) not in sys.path:
    sys.path.append(str(SUBSCRIPTION_SRC))

from repository import SubscriptionRepository
from service import SubscriptionService


class SubscriptionServiceCrudTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp_dir.name) / "subscriptions.db")
        self.repository = SubscriptionRepository(self.db_path)
        self.service = SubscriptionService(self.repository)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_create_get_pause_resume_delete_subscription(self) -> None:
        created = self.service.create_subscription(
            source_url="https://example.com/flight",
            baggage_mode="checked_bag",
            reports_per_day=3,
            chat_id="chat-1",
        )

        fetched = self.service.get_subscription(str(created["id"]))
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched["source_url"], "https://example.com/flight")
        self.assertEqual(fetched["baggage_mode"], "checked_bag")
        self.assertEqual(fetched["reports_per_day"], 3)
        self.assertEqual(fetched["status"], "active")

        paused = self.service.pause_subscription(str(created["id"]))
        self.assertTrue(paused)
        self.assertEqual(self.service.get_subscription(str(created["id"]))["status"], "paused")

        resumed = self.service.resume_subscription(str(created["id"]))
        self.assertTrue(resumed)
        self.assertEqual(self.service.get_subscription(str(created["id"]))["status"], "active")

        deleted = self.service.delete_subscription(str(created["id"]))
        self.assertTrue(deleted)
        self.assertIsNone(self.service.get_subscription(str(created["id"])))

    def test_create_validates_fields(self) -> None:
        with self.assertRaises(ValueError):
            self.service.create_subscription("", "cabin_only", 1, chat_id="chat-1")
        with self.assertRaises(ValueError):
            self.service.create_subscription("https://example.com", "", 1, chat_id="chat-1")
        with self.assertRaises(ValueError):
            self.service.create_subscription("https://example.com", "cabin_only", 0, chat_id="chat-1")


if __name__ == "__main__":
    unittest.main()

