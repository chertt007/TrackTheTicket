"""Entry point for fast price provider service process startup."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api import create_server
from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging
from service import FastPriceProviderService


if __name__ == "__main__":
    settings = ServiceSettings.from_env("fast-price-provider-service")
    logger = configure_logging(settings.service_name, settings.log_level)
    server = create_server(settings, FastPriceProviderService())
    logger.info("Fast Price Provider Service starting on %s:%s", settings.host, settings.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Fast Price Provider Service shutdown requested")
    finally:
        server.server_close()
