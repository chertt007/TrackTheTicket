"""Entry point for airline discovery service process startup."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api import create_server
from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging
from service import AirlineDiscoveryService


if __name__ == "__main__":
    settings = ServiceSettings.from_env("airline-discovery-service")
    logger = configure_logging(settings.service_name, settings.log_level)
    server = create_server(settings, AirlineDiscoveryService())
    logger.info("Airline Discovery Service starting on %s:%s", settings.host, settings.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Airline Discovery Service shutdown requested")
    finally:
        server.server_close()
