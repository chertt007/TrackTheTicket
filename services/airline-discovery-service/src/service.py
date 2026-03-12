"""Business logic for airline discovery and metadata enrichment."""
from __future__ import annotations

from urllib.parse import urlparse


class AirlineDiscoveryService:
    """Resolve airline metadata by source URL and optional explicit hints."""

    _DOMAIN_DIRECTORY = {
        "lufthansa.com": ("LH", "Lufthansa"),
        "elal.com": ("LY", "El Al"),
        "ryanair.com": ("FR", "Ryanair"),
        "wizzair.com": ("W6", "Wizz Air"),
    }

    def discover(
        self,
        source_url: str,
        airline_code: str | None = None,
        airline_domain: str | None = None,
    ) -> dict[str, str | float]:
        """Discover airline identity from URL and optional request hints."""
        normalized_url = source_url.strip()
        if not normalized_url:
            raise ValueError("source_url is required")

        discovered_domain = (airline_domain or urlparse(normalized_url).netloc).lower().strip()
        discovered_domain = discovered_domain.removeprefix("www.")
        catalog_entry = self._DOMAIN_DIRECTORY.get(discovered_domain)

        if airline_code and airline_code.strip():
            code = airline_code.strip().upper()
            name = catalog_entry[1] if catalog_entry else "Unknown Airline"
            confidence = 0.9
        elif catalog_entry:
            code = catalog_entry[0]
            name = catalog_entry[1]
            confidence = 0.95
        else:
            code = "UNK"
            name = "Unknown Airline"
            confidence = 0.3

        return {
            "airline_code": code,
            "airline_name": name,
            "airline_domain": discovered_domain or "unknown",
            "confidence": confidence,
        }
