"""Business logic for synthetic browser-based direct checks."""
from __future__ import annotations


class BrowserAutomationService:
    """Execute deterministic direct-check simulation for strategy validation."""

    def run_direct_check(
        self,
        subscription_id: str,
        source_url: str,
        strategy_id: str,
        baggage_mode: str,
    ) -> dict[str, str | float | bool]:
        """Run a simulated browser automation direct price check."""
        if not subscription_id.strip():
            raise ValueError("subscription_id is required")
        if not source_url.strip():
            raise ValueError("source_url is required")
        if not strategy_id.strip():
            raise ValueError("strategy_id is required")

        signal = sum(ord(ch) for ch in f"{subscription_id}:{strategy_id}:{source_url}")
        base_price = 60 + float(signal % 240)
        baggage_markup = 20.0 if baggage_mode.strip().lower() == "checked_bag" else 0.0
        return {
            "subscription_id": subscription_id,
            "status": "ok",
            "currency": "EUR",
            "direct_price": round(base_price + baggage_markup, 2),
            "is_match_confirmed": True,
            "screenshot_url": f"https://cdn.local/screens/{subscription_id}.png",
        }
