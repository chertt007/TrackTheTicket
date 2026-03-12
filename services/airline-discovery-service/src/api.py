"""HTTP handlers for airline discovery operations."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server
from service import AirlineDiscoveryService


def create_app(settings: ServiceSettings, discovery_service: AirlineDiscoveryService) -> FastAPI:
    """Build FastAPI app for airline discovery endpoints."""
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

    @app.post("/discover-airline")
    def discover_airline(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Discover airline information for provided flight source."""
        try:
            result = discovery_service.discover(
                source_url=str(body.get("source_url", "")),
                airline_code=(str(body["airline_code"]) if "airline_code" in body else None),
                airline_domain=(str(body["airline_domain"]) if "airline_domain" in body else None),
            )
            return {"airline": result}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )

    return app


def create_server(settings: ServiceSettings, discovery_service: AirlineDiscoveryService):
    """Create uvicorn server wrapper for this service."""
    return create_uvicorn_server(create_app(settings, discovery_service), settings)
