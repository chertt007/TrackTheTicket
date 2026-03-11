from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

from bot_flow import TelegramConversationManager
from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_uvicorn_server


def create_app(settings: ServiceSettings, manager: TelegramConversationManager) -> FastAPI:
    app = FastAPI(title=settings.service_name, version=settings.app_version)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.service_name,
            "environment": settings.environment,
            "version": settings.app_version,
        }

    @app.post("/telegram/update")
    def telegram_update(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        try:
            chat_id = str(body.get("chat_id", "")).strip()
            text = str(body.get("text", ""))
            if not chat_id:
                raise ValueError("chat_id is required")
            return manager.handle_message(chat_id, text)
        except ValueError as exc:
            return JSONResponse(
                status_code=400, content={"error": "invalid_request", "message": str(exc)}
            )
        except RuntimeError as exc:
            return JSONResponse(
                status_code=502, content={"error": "upstream_error", "message": str(exc)}
            )

    return app


def create_server(settings: ServiceSettings, manager: TelegramConversationManager):
    app = create_app(settings, manager)
    return create_uvicorn_server(app, settings)
