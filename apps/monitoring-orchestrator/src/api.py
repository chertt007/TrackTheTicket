"""HTTP handlers for triggering orchestrated monitoring runs."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from orchestrator import MonitoringOrchestrator
from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server


def create_app(settings: ServiceSettings, orchestrator: MonitoringOrchestrator) -> FastAPI:
    """Build FastAPI app for orchestrator endpoints."""
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

    @app.post("/run-check")
    def run_check(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Run a complete dual-source monitoring pipeline check."""
        try:
            return {"result": orchestrator.run_check(body)}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )
        except RuntimeError as exc:
            return JSONResponse(
                status_code=502,
                content={"error": "upstream_error", "message": str(exc)},
            )

    return app


def create_server(settings: ServiceSettings, orchestrator: MonitoringOrchestrator):
    """Create uvicorn server wrapper for this app."""
    return create_uvicorn_server(create_app(settings, orchestrator), settings)
