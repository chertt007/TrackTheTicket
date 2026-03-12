"""Tests for step-4 pipeline service business logic modules."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name: str, file_path: Path):
    """Load module by absolute file path to avoid import-name collisions."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Step4PipelineServiceTests(unittest.TestCase):
    """Validate basic behavior of step-4 service logic classes."""

    def test_flight_extraction_normalizes_payload(self) -> None:
        """Verify scenario: flight extraction normalizes payload."""
        module = load_module(
            "flight_extraction_service",
            ROOT / "services" / "flight-extraction-service" / "src" / "service.py",
        )
        service = module.FlightExtractionService()

        result = service.extract_flight(
            {
                "source_url": "https://example.com/search",
                "origin": "tlv",
                "destination": "ber",
                "passengers": 2,
            }
        )

        self.assertEqual(result["origin"], "TLV")
        self.assertEqual(result["destination"], "BER")
        self.assertEqual(result["passengers"], 2)
        self.assertTrue(result["normalized"])

    def test_airline_discovery_resolves_known_domain(self) -> None:
        """Verify scenario: airline discovery resolves known domain."""
        module = load_module(
            "airline_discovery_service",
            ROOT / "services" / "airline-discovery-service" / "src" / "service.py",
        )
        service = module.AirlineDiscoveryService()

        result = service.discover("https://www.lufthansa.com/de/en")
        self.assertEqual(result["airline_code"], "LH")
        self.assertEqual(result["airline_name"], "Lufthansa")

    def test_fast_and_direct_checks_return_prices(self) -> None:
        """Verify scenario: fast and direct checks return prices."""
        fast_module = load_module(
            "fast_price_provider_service",
            ROOT / "services" / "fast-price-provider-service" / "src" / "service.py",
        )
        direct_module = load_module(
            "browser_automation_service",
            ROOT / "services" / "browser-automation-service" / "src" / "service.py",
        )

        fast_service = fast_module.FastPriceProviderService()
        direct_service = direct_module.BrowserAutomationService()

        fast_result = fast_service.check_price("sub-1", "https://example.com", "checked_bag")
        direct_result = direct_service.run_direct_check(
            "sub-1",
            "https://example.com",
            "lh-default-v1",
            "checked_bag",
        )

        self.assertEqual(fast_result["status"], "ok")
        self.assertEqual(direct_result["status"], "ok")
        self.assertGreater(float(fast_result["price"]), 0)
        self.assertGreater(float(direct_result["direct_price"]), 0)

    def test_notification_service_validates_message(self) -> None:
        """Verify scenario: notification service validates message."""
        module = load_module(
            "notification_service",
            ROOT / "services" / "notification-service" / "src" / "service.py",
        )
        service = module.NotificationService()

        result = service.send_notification("chat-1", "hello")
        self.assertEqual(result["status"], "sent")

        with self.assertRaises(ValueError):
            service.send_notification("chat-1", "")


if __name__ == "__main__":
    unittest.main()
