# subscription-service

CRUD сервис подписок на FastAPI.

## Запуск

```bash
python src/main.py
```

## Endpoint

- `GET /health`
- `POST /subscriptions`
- `GET /subscriptions/{id}`
- `PATCH /subscriptions/{id}` (`action = pause|resume`)
- `DELETE /subscriptions/{id}`
