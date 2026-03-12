"""HTTP handlers for flight extraction operations."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server
from service import FlightExtractionService


def create_app(settings: ServiceSettings, extraction_service: FlightExtractionService) -> FastAPI:
    """Build FastAPI app for flight extraction endpoints."""
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

    @app.post("/extract-flight")
    def extract_flight(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Extract and normalize flight data from user payload."""
        try:
            return {"flight": extraction_service.extract_flight(body)}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )

    return app


def create_server(settings: ServiceSettings, extraction_service: FlightExtractionService):
    """Create uvicorn server wrapper for this service."""
    return create_uvicorn_server(create_app(settings, extraction_service), settings)
