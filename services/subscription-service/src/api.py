from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Type
from urllib.parse import urlparse

from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging
from service import SubscriptionService


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    raw_length = handler.headers.get("Content-Length", "0")
    length = int(raw_length) if raw_length.isdigit() else 0
    raw_data = handler.rfile.read(length) if length > 0 else b"{}"
    return json.loads(raw_data.decode("utf-8"))


def make_subscription_handler(
    settings: ServiceSettings, subscription_service: SubscriptionService
) -> Type[BaseHTTPRequestHandler]:
    logger = configure_logging(settings.service_name, settings.log_level)

    class SubscriptionHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                _json_response(
                    self,
                    200,
                    {
                        "status": "ok",
                        "service": settings.service_name,
                        "environment": settings.environment,
                        "version": settings.app_version,
                    },
                )
                return

            subscription_id = _extract_subscription_id(parsed.path)
            if subscription_id is None:
                _json_response(self, 404, {"error": "not_found"})
                return

            subscription = subscription_service.get_subscription(subscription_id)
            if subscription is None:
                _json_response(self, 404, {"error": "subscription_not_found"})
                return
            _json_response(self, 200, {"subscription": subscription})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != "/subscriptions":
                _json_response(self, 404, {"error": "not_found"})
                return

            try:
                body = _read_json(self)
                created = subscription_service.create_subscription(
                    source_url=str(body.get("source_url", "")),
                    baggage_mode=str(body.get("baggage_mode", "")),
                    reports_per_day=int(body.get("reports_per_day", 0)),
                    chat_id=str(body["chat_id"]) if "chat_id" in body else None,
                )
            except (ValueError, json.JSONDecodeError) as exc:
                _json_response(self, 400, {"error": "invalid_request", "message": str(exc)})
                return

            _json_response(
                self,
                201,
                {
                    "subscription_id": created["id"],
                    "status": created["status"],
                    "created_at": created["created_at"],
                },
            )

        def do_PATCH(self) -> None:  # noqa: N802
            subscription_id = _extract_subscription_id(urlparse(self.path).path)
            if subscription_id is None:
                _json_response(self, 404, {"error": "not_found"})
                return
            try:
                body = _read_json(self)
            except json.JSONDecodeError as exc:
                _json_response(self, 400, {"error": "invalid_request", "message": str(exc)})
                return

            action = str(body.get("action", "")).lower()
            if action == "pause":
                updated = subscription_service.pause_subscription(subscription_id)
            elif action == "resume":
                updated = subscription_service.resume_subscription(subscription_id)
            else:
                _json_response(self, 400, {"error": "invalid_action"})
                return

            if not updated:
                _json_response(self, 404, {"error": "subscription_not_found"})
                return

            subscription = subscription_service.get_subscription(subscription_id)
            _json_response(self, 200, {"subscription": subscription})

        def do_DELETE(self) -> None:  # noqa: N802
            subscription_id = _extract_subscription_id(urlparse(self.path).path)
            if subscription_id is None:
                _json_response(self, 404, {"error": "not_found"})
                return

            deleted = subscription_service.delete_subscription(subscription_id)
            if not deleted:
                _json_response(self, 404, {"error": "subscription_not_found"})
                return
            _json_response(self, 200, {"status": "deleted", "subscription_id": subscription_id})

        def log_message(self, fmt: str, *args: object) -> None:
            logger.info("%s - %s", self.address_string(), fmt % args)

    return SubscriptionHandler


def _extract_subscription_id(path: str) -> str | None:
    if not path.startswith("/subscriptions/"):
        return None
    parts = path.split("/")
    if len(parts) != 3 or not parts[2]:
        return None
    return parts[2]


def create_server(
    settings: ServiceSettings, subscription_service: SubscriptionService
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(
        (settings.host, settings.port),
        make_subscription_handler(settings, subscription_service),
    )

