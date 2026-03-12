"""Business logic for normalizing flight search payloads."""
from __future__ import annotations

from typing import Any


class FlightExtractionService:
    """Normalize flight parameters into a canonical internal payload."""

    def extract_flight(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Extract normalized flight details from raw request payload."""
        source_url = str(payload.get("source_url", "")).strip()
        if not source_url:
            raise ValueError("source_url is required")

        origin = str(payload.get("origin", "UNK")).strip().upper()
        destination = str(payload.get("destination", "UNK")).strip().upper()
        departure_date = str(payload.get("departure_date", "")).strip() or None
        return_date = str(payload.get("return_date", "")).strip() or None
        passengers = int(payload.get("passengers", 1))

        return {
            "source_url": source_url,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": passengers,
            "normalized": True,
        }
