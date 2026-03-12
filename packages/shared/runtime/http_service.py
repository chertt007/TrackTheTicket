"""Shared infrastructure utilities used by multiple modules."""
from __future__ import annotations

from fastapi import FastAPI
import uvicorn

from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging


class UvicornServerWrapper:
    def __init__(self, app: FastAPI, settings: ServiceSettings) -> None:
        """Initialize object state and dependencies."""
        self._logger = configure_logging(settings.service_name, settings.log_level)
        self._server = uvicorn.Server(
            uvicorn.Config(
                app=app,
                host=settings.host,
                port=settings.port,
                log_level=settings.log_level.lower(),
                access_log=False,
            )
        )

    def serve_forever(self) -> None:
        """Start serving requests until shutdown is requested."""
        self._logger.info("Service started")
        self._server.run()

    def shutdown(self) -> None:
        """Request graceful server shutdown."""
        self._server.should_exit = True

    def server_close(self) -> None:
        """Close server resources."""
        return


def create_health_app(settings: ServiceSettings) -> FastAPI:
    """Create health app."""
    app = FastAPI(title=settings.service_name, version=settings.app_version)

    @app.get("/health")
    def health() -> dict[str, str]:
        """Return service health metadata."""
        return {
            "status": "ok",
            "service": settings.service_name,
            "environment": settings.environment,
            "version": settings.app_version,
        }

    return app


def create_http_server(settings: ServiceSettings) -> UvicornServerWrapper:
    """Create http server."""
    return UvicornServerWrapper(create_health_app(settings), settings)


def create_uvicorn_server(app: FastAPI, settings: ServiceSettings) -> UvicornServerWrapper:
    """Create uvicorn server."""
    return UvicornServerWrapper(app, settings)


def run_service(settings: ServiceSettings) -> None:
    """Run service."""
    server = create_http_server(settings)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger = configure_logging(settings.service_name, settings.log_level)
        logger.info("Service shutdown requested")
    finally:
        server.server_close()
