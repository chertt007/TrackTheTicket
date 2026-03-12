"""Tests for monitoring orchestrator pipeline composition logic."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name: str, file_path: Path):
    """Load module by absolute file path for isolated test imports."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MonitoringOrchestratorTests(unittest.TestCase):
    """Validate that orchestrator combines step outputs into one summary."""

    def test_run_check_combines_pipeline_results(self) -> None:
        """Verify scenario: run check combines pipeline results."""
        http_client_module = load_module(
            "monitoring_http_client_module",
            ROOT / "apps" / "monitoring-orchestrator" / "src" / "http_client.py",
        )
        sys.modules["http_client"] = http_client_module
        module = load_module(
            "monitoring_orchestrator_module",
            ROOT / "apps" / "monitoring-orchestrator" / "src" / "orchestrator.py",
        )

        class FakeHttpClient:
            """Return deterministic responses for all pipeline service calls."""

            def post_json(self, base_url, path, payload):
                """Return canned JSON response by endpoint path."""
                if path == "/extract-flight":
                    return {"flight": {"origin": "TLV", "destination": "BER"}}
                if path == "/discover-airline":
                    return {"airline": {"airline_code": "LH", "airline_domain": "lufthansa.com"}}
                if path == "/fast-check":
                    return {"result": {"price": 140.0, "currency": "EUR"}}
                if path == "/strategies/resolve":
                    return {"strategy": {"strategy_id": "lh-default-v1"}}
                if path == "/direct-check":
                    return {
                        "result": {
                            "direct_price": 133.0,
                            "currency": "EUR",
                            "status": "ok",
                            "is_match_confirmed": True,
                            "screenshot_url": "https://cdn.local/s.png",
                        }
                    }
                if path == "/notifications/send":
                    return {"notification": {"status": "sent", "notification_id": "n-1"}}
                raise RuntimeError(f"Unexpected path: {path}")

        orchestrator = module.MonitoringOrchestrator(FakeHttpClient())
        result = orchestrator.run_check(
            {
                "subscription_id": "sub-1",
                "source_url": "https://example.com",
                "baggage_mode": "checked_bag",
                "chat_id": "tg-1",
            }
        )

        self.assertEqual(result["better_source"], "direct")
        self.assertIn("Fast=140.00", result["summary"])
        self.assertEqual(result["notification"]["status"], "sent")


if __name__ == "__main__":
    unittest.main()
