from __future__ import annotations

from fastapi import FastAPI
import uvicorn

from packages.shared.config.settings import ServiceSettings
from packages.shared.logging.logger import configure_logging


class UvicornServerWrapper:
    def __init__(self, app: FastAPI, settings: ServiceSettings) -> None:
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
        self._logger.info("Service started")
        self._server.run()

    def shutdown(self) -> None:
        self._server.should_exit = True

    def server_close(self) -> None:
        return


def create_health_app(settings: ServiceSettings) -> FastAPI:
    app = FastAPI(title=settings.service_name, version=settings.app_version)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.service_name,
            "environment": settings.environment,
            "version": settings.app_version,
        }

    return app


def create_http_server(settings: ServiceSettings) -> UvicornServerWrapper:
    return UvicornServerWrapper(create_health_app(settings), settings)


def create_uvicorn_server(app: FastAPI, settings: ServiceSettings) -> UvicornServerWrapper:
    return UvicornServerWrapper(app, settings)


def run_service(settings: ServiceSettings) -> None:
    server = create_http_server(settings)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger = configure_logging(settings.service_name, settings.log_level)
        logger.info("Service shutdown requested")
    finally:
        server.server_close()
