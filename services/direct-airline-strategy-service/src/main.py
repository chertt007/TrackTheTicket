"""Entry point for direct airline strategy service process startup."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api import create_server
from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging
from service import DirectAirlineStrategyService


if __name__ == "__main__":
    settings = ServiceSettings.from_env("direct-airline-strategy-service")
    logger = configure_logging(settings.service_name, settings.log_level)
    server = create_server(settings, DirectAirlineStrategyService())
    logger.info("Direct Airline Strategy Service starting on %s:%s", settings.host, settings.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Direct Airline Strategy Service shutdown requested")
    finally:
        server.server_close()
