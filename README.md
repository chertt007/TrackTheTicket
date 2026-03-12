# TTT Monorepo

Monorepo of services for dual-source airline ticket price monitoring.

## API stack

- Python 3.10+
- FastAPI
- Uvicorn
- SQLite (MVP for subscription-service)

## Quick start

```bash
python -m pytest -q
```

Run a service (example):

```bash
python services/subscription-service/src/main.py
```

## Documentation

- `docs/architecture/monorepo-structure.md`
- `docs/architecture/implementation-order.md`
- `docs/architecture/system-flow.md`
- `docs/implementation_step1.md`
- `docs/implementation_step2.md`
- `docs/implementation_step3.md`
- `docs/implementation_step4.md`

## API

Base endpoint implemented in all services/apps:

- `GET /health`

Current functional endpoints:

- Subscription Service:
  - `POST /subscriptions`
  - `GET /subscriptions/{id}`
  - `PATCH /subscriptions/{id}` (`action = pause|resume`)
  - `DELETE /subscriptions/{id}`
- Telegram Bot:
  - `POST /telegram/update`
- Flight Extraction Service:
  - `POST /extract-flight`
- Airline Discovery Service:
  - `POST /discover-airline`
- Fast Price Provider Service:
  - `POST /fast-check`
- Direct Airline Strategy Service:
  - `POST /strategies/resolve`
- Browser Automation Service:
  - `POST /direct-check`
- Notification Service:
  - `POST /notifications/send`
- AI Strategy Service:
  - `GET /ai/provider-config`
  - `POST /ai/select-model`
  - `POST /strategies/repair`
- Monitoring Orchestrator:
  - `POST /run-check`
