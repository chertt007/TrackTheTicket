# Порядок имплементации (Roadmap)

## 1. Foundation

- Единый API-стек: FastAPI + uvicorn.
- Шаблон сервиса: `src/main.py`, `tests`, `README.md`, `Dockerfile`.
- Health endpoint: `GET /health`.

## 2. Domain + Contracts + DB

- Доменные сущности.
- HTTP и event-контракты.
- Базовые миграции.

## 3. MVP: Subscription + Telegram

- CRUD подписок.
- Telegram диалог и команды управления.
- Интеграционные тесты end-to-end.

## 4. Остальные сервисы pipeline

- Flight Extraction
- Airline Discovery
- Fast Price Provider
- Direct Airline Strategy
- Browser Automation
- Monitoring Orchestrator
- Notification
- AI Strategy

## 5. Production readiness

- Контейнеризация, CI/CD, деплой.
- Мониторинг, алерты, отказоустойчивость.
