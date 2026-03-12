"""Tests for OpenRouter integration behavior in AI strategy service."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name: str, file_path: Path):
    """Load module by absolute file path for isolated imports in tests."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


CONSTANTS = load_module(
    "ai_model_constants_module",
    ROOT / "services" / "ai-strategy-service" / "src" / "model_constants.py",
)


class AiStrategyOpenRouterTests(unittest.TestCase):
    """Validate OpenRouter request parsing and local fallback paths."""

    def test_openrouter_client_uses_model_and_parses_json(self) -> None:
        """Verify scenario: openrouter client uses model and parses json."""
        module = load_module(
            "openrouter_client_module",
            ROOT / "services" / "ai-strategy-service" / "src" / "openrouter_client.py",
        )

        captured: dict[str, object] = {}

        def fake_requester(url, payload, headers):
            """Capture outgoing payload and return deterministic fake completion."""
            captured["url"] = url
            captured["payload"] = payload
            captured["headers"] = headers
            return {
                "choices": [
                    {
                        "message": {
                            "content": '{"strategy_json":"{\\"steps\\":[{\\"type\\":\\"extract\\"}]}","summary":"ok"}'
                        }
                    }
                ]
            }

        client = module.OpenRouterClient(
            api_key="test-key",
            model=CONSTANTS.ESCALATION_MODEL,
            requester=fake_requester,
        )

        result = client.generate_repair_plan("LH", "timeout", '{"steps":[]}')

        self.assertEqual(result["provider"], "openrouter")
        self.assertEqual(result["model"], CONSTANTS.ESCALATION_MODEL)
        self.assertEqual(result["summary"], "ok")
        self.assertIn("chat/completions", str(captured["url"]))

    def test_openrouter_client_allows_per_request_model_override(self) -> None:
        """Verify scenario: openrouter client allows per request model override."""
        module = load_module(
            "openrouter_client_module_override",
            ROOT / "services" / "ai-strategy-service" / "src" / "openrouter_client.py",
        )
        captured: dict[str, object] = {}

        def fake_requester(url, payload, headers):
            """Capture outgoing payload and return deterministic completion."""
            captured["payload"] = payload
            return {"choices": [{"message": {"content": '{"summary":"ok"}'}}]}

        client = module.OpenRouterClient(
            api_key="test-key",
            model=CONSTANTS.INTENT_EXTRACTION_MODEL,
            requester=fake_requester,
        )

        result = client.generate_repair_plan(
            "LH",
            "timeout",
            '{"steps":[]}',
            model=CONSTANTS.ESCALATION_MODEL,
        )
        self.assertEqual(result["model"], CONSTANTS.ESCALATION_MODEL)
        assert isinstance(captured["payload"], dict)
        self.assertEqual(captured["payload"]["model"], CONSTANTS.ESCALATION_MODEL)

    def test_ai_strategy_service_falls_back_when_openrouter_fails(self) -> None:
        """Verify scenario: ai strategy service falls back when openrouter fails."""
        openrouter_module = load_module(
            "openrouter_client_module_2",
            ROOT / "services" / "ai-strategy-service" / "src" / "openrouter_client.py",
        )
        sys.modules["openrouter_client"] = openrouter_module
        sys.modules["model_constants"] = CONSTANTS
        service_module = load_module(
            "ai_strategy_service_module",
            ROOT / "services" / "ai-strategy-service" / "src" / "service.py",
        )

        def failing_requester(url, payload, headers):
            """Raise runtime error to emulate provider failure."""
            raise RuntimeError("provider down")

        client = openrouter_module.OpenRouterClient(
            api_key="test-key",
            model=CONSTANTS.STRATEGY_REPAIR_MODEL,
            requester=failing_requester,
        )
        routing = service_module.ModelRoutingConfig(
            cheap_model=CONSTANTS.INTENT_EXTRACTION_MODEL,
            coding_model=CONSTANTS.STRATEGY_REPAIR_MODEL,
            robust_model=CONSTANTS.ESCALATION_MODEL,
            escalate_failure_count=2,
            escalate_confidence_threshold=0.75,
        )
        service = service_module.AiStrategyService(client, routing)

        result = service.repair_strategy("LH", "markup changed", '{"steps":[]}')
        self.assertEqual(result["provider"], "local-fallback")
        self.assertIn("fallback", result["summary"].lower())

    def test_ai_strategy_service_selects_cheap_and_robust_models(self) -> None:
        """Verify scenario: ai strategy service selects cheap and robust models."""
        sys.modules["model_constants"] = CONSTANTS
        service_module = load_module(
            "ai_strategy_service_module_2",
            ROOT / "services" / "ai-strategy-service" / "src" / "service.py",
        )

        routing = service_module.ModelRoutingConfig(
            cheap_model=CONSTANTS.INTENT_EXTRACTION_MODEL,
            coding_model=CONSTANTS.STRATEGY_REPAIR_MODEL,
            robust_model=CONSTANTS.ESCALATION_MODEL,
            escalate_failure_count=2,
            escalate_confidence_threshold=0.75,
        )
        service = service_module.AiStrategyService(openrouter_client=None, routing=routing)

        cheap = service.select_model(task_type="user_summary", failure_count=0, confidence=0.99)
        robust = service.select_model(task_type="strategy_repair", failure_count=3, confidence=0.8)

        self.assertEqual(cheap, CONSTANTS.INTENT_EXTRACTION_MODEL)
        self.assertEqual(robust, CONSTANTS.ESCALATION_MODEL)


if __name__ == "__main__":
    unittest.main()
