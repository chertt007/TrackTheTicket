from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Type

from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging


def make_handler(settings: ServiceSettings) -> Type[BaseHTTPRequestHandler]:
    logger = configure_logging(settings.service_name, settings.log_level)

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                payload = {
                    "status": "ok",
                    "service": settings.service_name,
                    "environment": settings.environment,
                    "version": settings.app_version,
                }
                data = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"not_found"}')

        def log_message(self, fmt: str, *args: object) -> None:
            logger.info("%s - %s", self.address_string(), fmt % args)

    return HealthHandler


def create_http_server(settings: ServiceSettings) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((settings.host, settings.port), make_handler(settings))


def run_service(settings: ServiceSettings) -> None:
    logger = configure_logging(settings.service_name, settings.log_level)
    server = create_http_server(settings)
    logger.info("Service started on %s:%s", settings.host, settings.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Service shutdown requested")
    finally:
        server.server_close()

