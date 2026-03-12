"""Module main."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import run_service


if __name__ == "__main__":
    settings = ServiceSettings.from_env("browser-automation-service")
    run_service(settings)
