"""HTTP client helpers for calling pipeline services from orchestrator."""
from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class JsonHttpClient:
    """Small JSON-over-HTTP helper with shared error handling semantics."""

    def post_json(self, base_url: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Send POST request and decode JSON response body."""
        url = f"{base_url.rstrip('/')}{path}"
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            raise RuntimeError(f"HTTP error from {url}: {exc.code} {body}") from exc
        except URLError as exc:
            raise RuntimeError(f"HTTP service unavailable at {url}: {exc.reason}") from exc
