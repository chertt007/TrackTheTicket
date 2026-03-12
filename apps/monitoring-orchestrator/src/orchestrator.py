"""Pipeline orchestration logic that coordinates all step-4 services."""
from __future__ import annotations

import os
from typing import Any

from http_client import JsonHttpClient


class MonitoringOrchestrator:
    """Coordinate fast and direct checks and emit final notification payloads."""

    def __init__(self, http_client: JsonHttpClient) -> None:
        """Initialize orchestrator with HTTP client dependency."""
        self.http_client = http_client
        self.flight_extraction_url = os.environ.get("FLIGHT_EXTRACTION_URL", "http://127.0.0.1:8011")
        self.airline_discovery_url = os.environ.get("AIRLINE_DISCOVERY_URL", "http://127.0.0.1:8012")
        self.fast_price_provider_url = os.environ.get("FAST_PRICE_PROVIDER_URL", "http://127.0.0.1:8013")
        self.strategy_service_url = os.environ.get("DIRECT_STRATEGY_URL", "http://127.0.0.1:8014")
        self.browser_automation_url = os.environ.get("BROWSER_AUTOMATION_URL", "http://127.0.0.1:8015")
        self.notification_service_url = os.environ.get("NOTIFICATION_SERVICE_URL", "http://127.0.0.1:8016")

    def run_check(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run full dual-source check pipeline and return reconciliation result."""
        subscription_id = str(payload.get("subscription_id", "")).strip()
        source_url = str(payload.get("source_url", "")).strip()
        baggage_mode = str(payload.get("baggage_mode", "cabin_only")).strip()
        chat_id = str(payload.get("chat_id", "")).strip()

        if not subscription_id:
            raise ValueError("subscription_id is required")
        if not source_url:
            raise ValueError("source_url is required")

        extracted = self.http_client.post_json(
            self.flight_extraction_url,
            "/extract-flight",
            {
                "source_url": source_url,
                "origin": payload.get("origin", "UNK"),
                "destination": payload.get("destination", "UNK"),
                "departure_date": payload.get("departure_date", ""),
                "return_date": payload.get("return_date", ""),
                "passengers": payload.get("passengers", 1),
            },
        )["flight"]

        airline = self.http_client.post_json(
            self.airline_discovery_url,
            "/discover-airline",
            {"source_url": source_url},
        )["airline"]

        fast_result = self.http_client.post_json(
            self.fast_price_provider_url,
            "/fast-check",
            {
                "subscription_id": subscription_id,
                "source_url": source_url,
                "baggage_mode": baggage_mode,
            },
        )["result"]

        strategy = self.http_client.post_json(
            self.strategy_service_url,
            "/strategies/resolve",
            {
                "airline_code": airline["airline_code"],
                "airline_domain": airline["airline_domain"],
            },
        )["strategy"]

        direct_result = self.http_client.post_json(
            self.browser_automation_url,
            "/direct-check",
            {
                "subscription_id": subscription_id,
                "source_url": source_url,
                "strategy_id": strategy["strategy_id"],
                "baggage_mode": baggage_mode,
            },
        )["result"]

        fast_price = float(fast_result["price"])
        direct_price = float(direct_result["direct_price"])
        better_source = "direct" if direct_price <= fast_price else "fast"
        delta = abs(direct_price - fast_price)

        summary = (
            f"Fast={fast_price:.2f} {fast_result['currency']}; "
            f"Direct={direct_price:.2f} {direct_result['currency']}; "
            f"better={better_source}; delta={delta:.2f}"
        )

        notification = None
        if chat_id:
            notification = self.http_client.post_json(
                self.notification_service_url,
                "/notifications/send",
                {
                    "chat_id": chat_id,
                    "message": summary,
                    "channel": "telegram",
                },
            )["notification"]

        return {
            "subscription_id": subscription_id,
            "extracted": extracted,
            "airline": airline,
            "fast_result": fast_result,
            "strategy": strategy,
            "direct_result": direct_result,
            "better_source": better_source,
            "summary": summary,
            "notification": notification,
        }
