"""Business logic for repairing airline strategies with AI or local fallback."""
from __future__ import annotations

import os
from dataclasses import dataclass

from model_constants import (
    INTENT_EXTRACTION_MODEL,
    ESCALATION_MODEL,
    SIMPLE_TASK_TYPES,
    STRATEGY_REPAIR_MODEL,
    STRATEGY_TASK_TYPES,
)
from openrouter_client import OpenRouterClient


@dataclass(frozen=True)
class ModelRoutingConfig:
    """Routing configuration for selecting cost/quality AI models by task context."""

    cheap_model: str
    coding_model: str
    robust_model: str
    escalate_failure_count: int
    escalate_confidence_threshold: float


class AiStrategyService:
    """Repair direct-airline strategies using OpenRouter or deterministic fallback."""

    def __init__(self, openrouter_client: OpenRouterClient | None, routing: ModelRoutingConfig) -> None:
        """Initialize service dependencies and default model metadata."""
        self.openrouter_client = openrouter_client
        self.routing = routing

    @classmethod
    def from_env(cls) -> "AiStrategyService":
        """Build service instance from environment variables."""
        legacy_model = os.environ.get("OPENROUTER_MODEL", "").strip()
        cheap_model = os.environ.get(
            "OPENROUTER_MODEL_CHEAP",
            legacy_model or INTENT_EXTRACTION_MODEL,
        ).strip()
        coding_model = os.environ.get(
            "OPENROUTER_MODEL_CODING",
            legacy_model or STRATEGY_REPAIR_MODEL,
        ).strip()
        robust_model = os.environ.get(
            "OPENROUTER_MODEL_ROBUST",
            ESCALATION_MODEL,
        ).strip()
        escalate_failure_count = int(os.environ.get("OPENROUTER_ESCALATE_FAILURE_COUNT", "2"))
        escalate_confidence_threshold = float(
            os.environ.get("OPENROUTER_ESCALATE_CONFIDENCE_THRESHOLD", "0.75")
        )
        api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        routing = ModelRoutingConfig(
            cheap_model=cheap_model,
            coding_model=coding_model,
            robust_model=robust_model,
            escalate_failure_count=escalate_failure_count,
            escalate_confidence_threshold=escalate_confidence_threshold,
        )

        client = None
        if api_key:
            client = OpenRouterClient(api_key=api_key, model=coding_model, base_url=base_url)

        return cls(openrouter_client=client, routing=routing)

    def select_model(
        self,
        task_type: str,
        failure_count: int = 0,
        confidence: float = 1.0,
        force_model: str | None = None,
    ) -> str:
        """Select model according to task complexity and escalation signals."""
        if force_model and force_model.strip():
            return force_model.strip()

        task = task_type.strip().lower() if task_type.strip() else "strategy_repair"

        if task in SIMPLE_TASK_TYPES:
            selected = self.routing.cheap_model
        elif task in STRATEGY_TASK_TYPES:
            selected = self.routing.coding_model
        else:
            selected = self.routing.coding_model

        if (
            failure_count >= self.routing.escalate_failure_count
            or confidence < self.routing.escalate_confidence_threshold
        ):
            selected = self.routing.robust_model

        return selected

    def repair_strategy(
        self,
        airline_code: str,
        failure_reason: str,
        current_strategy_json: str,
        task_type: str = "strategy_repair",
        failure_count: int = 0,
        confidence: float = 1.0,
        force_model: str | None = None,
    ) -> dict[str, str]:
        """Repair strategy using OpenRouter when configured, otherwise use fallback."""
        if not airline_code.strip():
            raise ValueError("airline_code is required")
        if not failure_reason.strip():
            raise ValueError("failure_reason is required")

        normalized_current = current_strategy_json.strip() or '{"steps":[]}'

        selected_model = self.select_model(
            task_type=task_type,
            failure_count=failure_count,
            confidence=confidence,
            force_model=force_model,
        )

        if self.openrouter_client is not None:
            try:
                return self.openrouter_client.generate_repair_plan(
                    airline_code=airline_code.strip().upper(),
                    failure_reason=failure_reason.strip(),
                    current_strategy_json=normalized_current,
                    model=selected_model,
                )
            except RuntimeError:
                if selected_model != self.routing.robust_model:
                    try:
                        return self.openrouter_client.generate_repair_plan(
                            airline_code=airline_code.strip().upper(),
                            failure_reason=failure_reason.strip(),
                            current_strategy_json=normalized_current,
                            model=self.routing.robust_model,
                        )
                    except RuntimeError:
                        pass

        return {
            "strategy_json": (
                '{"steps":[{"type":"navigate"},{"type":"search"},{"type":"extract_price"}],'
                '"note":"fallback_repair"}'
            ),
            "summary": "Local fallback strategy generated because OpenRouter is not configured or failed.",
            "provider": "local-fallback",
            "model": selected_model,
        }
