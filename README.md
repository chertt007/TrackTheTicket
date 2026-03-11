# TTT Monorepo

Монорепозиторий сервисов для dual-source мониторинга цен авиабилетов.

## Технологический стек API

- Python 3.10+
- FastAPI
- Uvicorn
- SQLite (для MVP subscription-service)

## Быстрый старт

```bash
python -m unittest discover -s tests -v
```

Запуск отдельного сервиса (пример):

```bash
python services/subscription-service/src/main.py
```

## Документация

- `docs/architecture/monorepo-structure.md`
- `docs/architecture/implementation-order.md`
- `docs/architecture/system-flow.md`
- `docs/implementation_step1.md`
- `docs/implementation_step2.md`
- `docs/implementation_step3.md`

## API

Базовые HTTP endpoint'ы сервисов реализованы на FastAPI.

- Healthcheck: `GET /health`
- Subscription Service:
  - `POST /subscriptions`
  - `GET /subscriptions/{id}`
  - `PATCH /subscriptions/{id}` (`action = pause|resume`)
  - `DELETE /subscriptions/{id}`
- Telegram Bot:
  - `POST /telegram/update`
