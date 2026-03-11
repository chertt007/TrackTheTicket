from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class SubscriptionApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def create_subscription(
        self, source_url: str, baggage_mode: str, reports_per_day: int, chat_id: str
    ) -> dict[str, Any]:
        payload = {
            "source_url": source_url,
            "baggage_mode": baggage_mode,
            "reports_per_day": reports_per_day,
            "chat_id": chat_id,
        }
        return self._request("POST", "/subscriptions", payload)

    def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        return self._request("GET", f"/subscriptions/{subscription_id}")

    def pause_subscription(self, subscription_id: str) -> dict[str, Any]:
        return self._request("PATCH", f"/subscriptions/{subscription_id}", {"action": "pause"})

    def resume_subscription(self, subscription_id: str) -> dict[str, Any]:
        return self._request("PATCH", f"/subscriptions/{subscription_id}", {"action": "resume"})

    def delete_subscription(self, subscription_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/subscriptions/{subscription_id}")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            raise RuntimeError(f"Subscription API error {exc.code}: {body}") from exc
        except URLError as exc:
            raise RuntimeError(f"Subscription API unavailable: {exc.reason}") from exc

