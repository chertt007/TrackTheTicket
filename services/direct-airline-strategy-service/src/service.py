"""Business logic for selecting direct-airline automation strategy."""
from __future__ import annotations


class DirectAirlineStrategyService:
    """Resolve active direct-check strategy by airline identity."""

    _STRATEGIES = {
        "LH": {
            "strategy_id": "lh-default-v1",
            "airline_code": "LH",
            "strategy_version": 1,
            "playwright_script": "open-home;accept-cookies;fill-search;extract-price",
        },
        "LY": {
            "strategy_id": "ly-default-v1",
            "airline_code": "LY",
            "strategy_version": 1,
            "playwright_script": "open-home;fill-search;extract-price",
        },
    }

    def resolve_strategy(self, airline_code: str, airline_domain: str) -> dict[str, str | int]:
        """Resolve strategy metadata for given airline code or domain hint."""
        code = airline_code.strip().upper() if airline_code.strip() else "UNK"
        strategy = self._STRATEGIES.get(code)
        if strategy:
            return dict(strategy)

        domain_slug = airline_domain.strip().lower().replace(".", "-") if airline_domain.strip() else "unknown"
        return {
            "strategy_id": f"fallback-{domain_slug}-v1",
            "airline_code": code,
            "strategy_version": 1,
            "playwright_script": "open-home;fill-search;extract-price",
        }
