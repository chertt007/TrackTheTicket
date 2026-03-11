# Шаг 2. Доменная модель, контракты и миграции

Документ фиксирует реализацию второго этапа: доменные сущности, межсервисные контракты и стартовая схема БД.

## 1. Цель шага

- Формализовать модель данных для dual-source мониторинга.
- Зафиксировать HTTP DTO и event-сообщения для межсервисной интеграции.
- Добавить миграцию, применяемую на чистой БД без ручных действий.

## 2. Что реализовано

## 2.1 Доменные сущности

Добавлен пакет моделей:
- [packages/domain/models/subscription.py](C:/Git/TTT/packages/domain/models/subscription.py)
- [packages/domain/models/direct_airline_strategy.py](C:/Git/TTT/packages/domain/models/direct_airline_strategy.py)
- [packages/domain/models/check_job.py](C:/Git/TTT/packages/domain/models/check_job.py)
- [packages/domain/models/check_result.py](C:/Git/TTT/packages/domain/models/check_result.py)

Особенности:
- Каждая сущность реализована как `dataclass(frozen=True)`.
- Добавлены `to_dict()` / `from_dict()` для явной сериализации.
- Даты сериализуются в ISO-формат (`datetime.isoformat()`).

## 2.2 HTTP-контракты

Добавлены DTO:
- [packages/contracts/http/dtos.py](C:/Git/TTT/packages/contracts/http/dtos.py)

Реализованы:
- `CreateSubscriptionRequest`
- `CreateSubscriptionResponse`
- `CheckResultResponse`

## 2.3 Event-контракты

Добавлены event-сообщения:
- [packages/contracts/events/messages.py](C:/Git/TTT/packages/contracts/events/messages.py)

Реализованы:
- `FastCheckCompletedEvent`
- `DirectCheckCompletedEvent`
- `ReconcileAndNotifyRequestedEvent`

## 2.4 Стартовая миграция БД

Добавлена миграция:
- [infra/migrations/0001_initial_schema.sql](C:/Git/TTT/infra/migrations/0001_initial_schema.sql)

Создаются таблицы:
- `subscription`
- `direct_airline_strategy`
- `check_job`
- `check_result`

Также добавлены базовые индексы по ключевым полям фильтрации/джойнов.

## 3. Тесты

Добавлены и проходят:
- [tests/test_domain_serialization.py](C:/Git/TTT/tests/test_domain_serialization.py)
- [tests/test_contracts_serialization.py](C:/Git/TTT/tests/test_contracts_serialization.py)
- [tests/test_migration_schema.py](C:/Git/TTT/tests/test_migration_schema.py)

Команда проверки:

```bash
python -m unittest discover -s tests -v
```

Фактический результат:
- `Ran 11 tests`
- `OK`

## 4. Соответствие acceptance criteria шага 2

Статус:
- Сущности и контракты зафиксированы и версионированы в `packages/domain` и `packages/contracts`: выполнено.
- Миграция применяется на чистой БД: выполнено (проверено тестом на SQLite in-memory).
- Контрактные roundtrip-тесты сериализации/десериализации: выполнено.

## 5. Ограничения текущей реализации

- Контракты пока определены как Python-модели без OpenAPI/AsyncAPI схем.
- Миграции пока в одном SQL-файле без отдельного migration runner.
- Типы статусов пока строковые; строгие enum-ограничения можно усилить на следующем шаге.

## 6. Следующий шаг

Шаг 3: реализовать MVP-поток `Telegram Bot + Subscription Service` для полноценного создания/управления подпиской через бот-интерфейс.
