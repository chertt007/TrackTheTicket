from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api import create_server
from bot_flow import TelegramConversationManager
from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging
from subscription_client import SubscriptionApiClient


if __name__ == "__main__":
    settings = ServiceSettings.from_env("telegram-bot")
    logger = configure_logging(settings.service_name, settings.log_level)
    base_url = os.environ.get("SUBSCRIPTION_SERVICE_URL", "http://127.0.0.1:8001")
    manager = TelegramConversationManager(SubscriptionApiClient(base_url=base_url))
    server = create_server(settings, manager)
    logger.info("Telegram Bot started on %s:%s", settings.host, settings.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Telegram Bot shutdown requested")
    finally:
        server.server_close()

