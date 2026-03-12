"""HTTP handlers for notification delivery."""
from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server
from service import NotificationService


def create_app(settings: ServiceSettings, notification_service: NotificationService) -> FastAPI:
    """Build FastAPI app for notification endpoints."""
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

    @app.post("/notifications/send")
    def send_notification(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        """Send notification to the configured user channel."""
        try:
            result = notification_service.send_notification(
                chat_id=str(body.get("chat_id", "")),
                message=str(body.get("message", "")),
                channel=str(body.get("channel", "telegram")),
            )
            return {"notification": result}
        except (TypeError, ValueError) as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": str(exc)},
            )

    return app


def create_server(settings: ServiceSettings, notification_service: NotificationService):
    """Create uvicorn server wrapper for this service."""
    return create_uvicorn_server(create_app(settings, notification_service), settings)
