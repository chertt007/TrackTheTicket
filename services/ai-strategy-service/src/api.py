"""HTTP handlers for AI strategy repair operations."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server
from service import AiStrategyService


def create_app(settings: ServiceSettings, strategy_service: AiStrategyService) -> FastAPI:
    """Build FastAPI app for AI strategy endpoints."""
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

    @app.get("/ai/provider-config")
    def provider_config() -> dict[str, str | bool]:
        """Expose effective AI provider configuration without leaking secrets."""
        return {
            "provider": "openrouter",
            "configured": strategy_service.openrouter_client is not None,
            "cheap_model": strategy_service.routing.cheap_model,
            "coding_model": strategy_service.routing.coding_model,
            "robust_model": strategy_service.routing.robust_model,
            "escalate_failure_count": strategy_service.routing.escalate_failure_count,
            "escalate_confidence_threshold": strategy_service.routing.escalate_confidence_threshold,
        }

    @app.post("/ai/select-model")
    def select_model(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Return selected model for provided task and reliability signals."""
        try:
            selected = strategy_service.select_model(
                task_type=str(body.get("task_type", "strategy_repair")),
                failure_count=int(body.get("failure_count", 0)),
                confidence=float(body.get("confidence", 1.0)),
                force_model=(str(body["force_model"]) if "force_model" in body else None),
            )
            return {"model": selected}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )

    @app.post("/strategies/repair")
    def repair_strategy(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Repair strategy using OpenRouter model or local fallback."""
        try:
            result = strategy_service.repair_strategy(
                airline_code=str(body.get("airline_code", "")),
                failure_reason=str(body.get("failure_reason", "")),
                current_strategy_json=str(body.get("current_strategy_json", "")),
                task_type=str(body.get("task_type", "strategy_repair")),
                failure_count=int(body.get("failure_count", 0)),
                confidence=float(body.get("confidence", 1.0)),
                force_model=(str(body["force_model"]) if "force_model" in body else None),
            )
            return {"result": result}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )

    return app


def create_server(settings: ServiceSettings, strategy_service: AiStrategyService):
    """Create uvicorn server wrapper for this service."""
    return create_uvicorn_server(create_app(settings, strategy_service), settings)
