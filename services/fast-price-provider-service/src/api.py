"""HTTP handlers for fast price provider checks."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server
from service import FastPriceProviderService


def create_app(settings: ServiceSettings, price_service: FastPriceProviderService) -> FastAPI:
    """Build FastAPI app for fast-price endpoints."""
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

    @app.post("/fast-check")
    def fast_check(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Run fast-source price check for the provided subscription."""
        try:
            result = price_service.check_price(
                subscription_id=str(body.get("subscription_id", "")),
                source_url=str(body.get("source_url", "")),
                baggage_mode=str(body.get("baggage_mode", "cabin_only")),
            )
            return {"result": result}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )

    return app


def create_server(settings: ServiceSettings, price_service: FastPriceProviderService):
    """Create uvicorn server wrapper for this service."""
    return create_uvicorn_server(create_app(settings, price_service), settings)
