from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Type
from urllib.parse import urlparse

from bot_flow import TelegramConversationManager
from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging


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


def make_telegram_handler(
    settings: ServiceSettings, manager: TelegramConversationManager
) -> Type[BaseHTTPRequestHandler]:
    logger = configure_logging(settings.service_name, settings.log_level)

    class TelegramHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if urlparse(self.path).path == "/health":
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
            _json_response(self, 404, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/telegram/update":
                _json_response(self, 404, {"error": "not_found"})
                return

            try:
                body = _read_json(self)
                chat_id = str(body.get("chat_id", "")).strip()
                text = str(body.get("text", ""))
                if not chat_id:
                    raise ValueError("chat_id is required")
                result = manager.handle_message(chat_id, text)
                _json_response(self, 200, result)
            except (ValueError, json.JSONDecodeError) as exc:
                _json_response(self, 400, {"error": "invalid_request", "message": str(exc)})
            except RuntimeError as exc:
                _json_response(self, 502, {"error": "upstream_error", "message": str(exc)})

        def log_message(self, fmt: str, *args: object) -> None:
            logger.info("%s - %s", self.address_string(), fmt % args)

    return TelegramHandler


def create_server(
    settings: ServiceSettings, manager: TelegramConversationManager
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((settings.host, settings.port), make_telegram_handler(settings, manager))

