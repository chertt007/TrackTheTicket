from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api import create_server
from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging
from repository import SubscriptionRepository
from service import SubscriptionService


if __name__ == "__main__":
    settings = ServiceSettings.from_env("subscription-service")
    logger = configure_logging(settings.service_name, settings.log_level)
    db_path = os.environ.get("SUBSCRIPTION_DB_PATH", str(ROOT / "data" / "subscriptions.db"))
    repository = SubscriptionRepository(db_path=db_path)
    subscription_service = SubscriptionService(repository)
    server = create_server(settings, subscription_service)
    logger.info("Subscription Service starting on %s:%s", settings.host, settings.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Subscription Service shutdown requested")
    finally:
        server.server_close()
