# Шаг 3. Subscription Service + Telegram Bot (MVP)

## Цель

Сделать рабочий пользовательский поток создания и управления подпиской через Telegram-диалог.

## Реализовано

### Subscription Service

- FastAPI API:
  - `POST /subscriptions`
  - `GET /subscriptions/{id}`
  - `PATCH /subscriptions/{id}` (`action = pause|resume`)
  - `DELETE /subscriptions/{id}`
  - `GET /health`
- SQLite репозиторий для хранения подписок.
- Валидация `source_url`, `baggage_mode`, `reports_per_day`.

### Telegram Bot

- FastAPI webhook endpoint:
  - `POST /telegram/update`
  - `GET /health`
- Диалоговые команды:
  - `/new`
  - `/pause <subscription_id>`
  - `/resume <subscription_id>`
  - `/delete <subscription_id>`

## Проверка

```bash
python -m unittest discover -s tests -v
```

Покрывается:

- CRUD подписки;
- диалог создания подписки;
- команды pause/resume/delete.
