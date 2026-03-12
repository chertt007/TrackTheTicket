"""HTTP handlers for subscription CRUD operations."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server
from service import SubscriptionService


def create_app(settings: ServiceSettings, subscription_service: SubscriptionService) -> FastAPI:
    """Create app."""
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

    @app.get("/subscriptions/{subscription_id}")
    def get_subscription(subscription_id: str) -> dict[str, Any]:
        """Fetch subscription."""
        subscription = subscription_service.get_subscription(subscription_id)
        if subscription is None:
            return JSONResponse(status_code=404, content={"error": "subscription_not_found"})
        return {"subscription": subscription}

    @app.post("/subscriptions", status_code=201)
    def create_subscription(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Create subscription."""
        try:
            created = subscription_service.create_subscription(
                source_url=str(body.get("source_url", "")),
                baggage_mode=str(body.get("baggage_mode", "")),
                reports_per_day=int(body.get("reports_per_day", 0)),
                chat_id=str(body["chat_id"]) if "chat_id" in body else None,
            )
        except (ValueError, TypeError) as exc:
            return JSONResponse(
                status_code=400, content={"error": "invalid_request", "message": str(exc)}
            )

        return {
            "subscription_id": created["id"],
            "status": created["status"],
            "created_at": created["created_at"],
        }

    @app.patch("/subscriptions/{subscription_id}")
    def update_subscription(
        subscription_id: str, body: dict[str, Any] = Body(default_factory=dict)
    ) -> dict[str, Any]:
        """Update subscription."""
        action = str(body.get("action", "")).lower()
        if action == "pause":
            updated = subscription_service.pause_subscription(subscription_id)
        elif action == "resume":
            updated = subscription_service.resume_subscription(subscription_id)
        else:
            return JSONResponse(status_code=400, content={"error": "invalid_action"})

        if not updated:
            return JSONResponse(status_code=404, content={"error": "subscription_not_found"})

        subscription = subscription_service.get_subscription(subscription_id)
        return {"subscription": subscription}

    @app.delete("/subscriptions/{subscription_id}")
    def delete_subscription(subscription_id: str) -> dict[str, str]:
        """Delete subscription."""
        deleted = subscription_service.delete_subscription(subscription_id)
        if not deleted:
            return JSONResponse(status_code=404, content={"error": "subscription_not_found"})
        return {"status": "deleted", "subscription_id": subscription_id}

    return app


def create_server(settings: ServiceSettings, subscription_service: SubscriptionService):
    """Create server."""
    app = create_app(settings, subscription_service)
    return create_uvicorn_server(app, settings)
