"""Business logic for deterministic fast-source price checks."""
from __future__ import annotations


class FastPriceProviderService:
    """Return a quick synthetic price result for a subscription request."""

    def check_price(self, subscription_id: str, source_url: str, baggage_mode: str) -> dict[str, str | float]:
        """Compute deterministic fast-source price snapshot."""
        if not subscription_id.strip():
            raise ValueError("subscription_id is required")
        if not source_url.strip():
            raise ValueError("source_url is required")

        signal = sum(ord(ch) for ch in f"{subscription_id}:{source_url}:{baggage_mode}")
        base_price = 70 + float(signal % 250)
        baggage_markup = 25.0 if baggage_mode.strip().lower() == "checked_bag" else 0.0
        return {
            "subscription_id": subscription_id,
            "status": "ok",
            "provider": "synthetic-fast-provider",
            "currency": "EUR",
            "price": round(base_price + baggage_markup, 2),
        }
