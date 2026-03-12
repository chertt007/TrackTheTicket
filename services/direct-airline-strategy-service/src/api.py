"""HTTP handlers for direct-airline strategy resolution."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server
from service import DirectAirlineStrategyService


def create_app(settings: ServiceSettings, strategy_service: DirectAirlineStrategyService) -> FastAPI:
    """Build FastAPI app for strategy resolution endpoints."""
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

    @app.post("/strategies/resolve")
    def resolve_strategy(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Resolve direct strategy for requested airline context."""
        try:
            strategy = strategy_service.resolve_strategy(
                airline_code=str(body.get("airline_code", "")),
                airline_domain=str(body.get("airline_domain", "")),
            )
            return {"strategy": strategy}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )

    return app


def create_server(settings: ServiceSettings, strategy_service: DirectAirlineStrategyService):
    """Create uvicorn server wrapper for this service."""
    return create_uvicorn_server(create_app(settings, strategy_service), settings)
