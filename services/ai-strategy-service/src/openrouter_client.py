"""OpenRouter API client for strategy-repair completions."""
from __future__ import annotations

import json
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OpenRouterClient:
    """Minimal OpenRouter chat-completions client with injectable requester for tests."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1",
        app_name: str = "TTT-Monorepo",
        requester: Callable[[str, dict[str, Any], dict[str, str]], dict[str, Any]] | None = None,
    ) -> None:
        """Initialize OpenRouter connection settings and optional custom requester."""
        if not api_key.strip():
            raise ValueError("OPENROUTER_API_KEY is required")
        if not model.strip():
            raise ValueError("OPENROUTER_MODEL is required")

        self.api_key = api_key.strip()
        self.model = model.strip()
        self.base_url = base_url.rstrip("/")
        self.app_name = app_name
        self._requester = requester

    def generate_repair_plan(
        self,
        airline_code: str,
        failure_reason: str,
        current_strategy_json: str,
        model: str | None = None,
    ) -> dict[str, str]:
        """Generate strategy repair guidance from OpenRouter model response."""
        effective_model = model.strip() if model and model.strip() else self.model
        prompt = (
            "Return compact JSON with keys strategy_json and summary. "
            f"airline_code={airline_code}; failure_reason={failure_reason}; "
            f"current_strategy={current_strategy_json}"
        )
        payload = {
            "model": effective_model,
            "messages": [
                {"role": "system", "content": "You repair flight scraping strategies."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ttt.local",
            "X-Title": self.app_name,
        }

        response = self._post_json(f"{self.base_url}/chat/completions", payload, headers)
        content = self._extract_content(response)
        parsed = self._try_parse_json(content)

        return {
            "strategy_json": parsed.get("strategy_json", current_strategy_json),
            "summary": parsed.get("summary", content),
            "provider": "openrouter",
            "model": effective_model,
        }

    def _post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Send JSON POST request using injected requester or urllib fallback."""
        if self._requester is not None:
            return self._requester(url, payload, headers)

        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers=headers,
        )
        try:
            with urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            raise RuntimeError(f"OpenRouter request failed {exc.code}: {body}") from exc
        except URLError as exc:
            raise RuntimeError(f"OpenRouter is unreachable: {exc.reason}") from exc

    def _extract_content(self, response: dict[str, Any]) -> str:
        """Extract assistant content text from OpenRouter completion payload."""
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("OpenRouter response does not contain choices")

        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenRouter response content is empty")
        return content.strip()

    def _try_parse_json(self, content: str) -> dict[str, str]:
        """Parse model content as JSON and fallback to summary-only payload."""
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return {str(k): str(v) for k, v in parsed.items()}
        except json.JSONDecodeError:
            pass
        return {"summary": content}
