# Шаг 2. Доменная модель, контракты и миграции

## Цель

Формализовать модель данных, контракты обмена и SQL-схему для сервисов.

## Реализовано

- Доменные сущности в `packages/domain/models`.
- HTTP DTO в `packages/contracts/http/dtos.py`.
- Event-контракты в `packages/contracts/events/messages.py`.
- Базовая SQL-миграция в `infra/migrations/0001_initial_schema.sql`.

## Проверка

```bash
python -m unittest discover -s tests -v
```

Покрывается:

- сериализация/десериализация доменных моделей;
- сериализация/десериализация контрактов;
- применимость SQL-схемы.

## Примечание по API

Сервисный HTTP слой в проекте унифицирован на FastAPI.
