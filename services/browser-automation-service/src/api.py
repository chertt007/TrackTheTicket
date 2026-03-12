"""HTTP handlers for browser automation checks."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server
from service import BrowserAutomationService


def create_app(settings: ServiceSettings, automation_service: BrowserAutomationService) -> FastAPI:
    """Build FastAPI app for browser automation endpoints."""
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

    @app.post("/direct-check")
    def direct_check(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Execute direct browser-based check with resolved strategy."""
        try:
            result = automation_service.run_direct_check(
                subscription_id=str(body.get("subscription_id", "")),
                source_url=str(body.get("source_url", "")),
                strategy_id=str(body.get("strategy_id", "")),
                baggage_mode=str(body.get("baggage_mode", "cabin_only")),
            )
            return {"result": result}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )

    return app


def create_server(settings: ServiceSettings, automation_service: BrowserAutomationService):
    """Create uvicorn server wrapper for this service."""
    return create_uvicorn_server(create_app(settings, automation_service), settings)
