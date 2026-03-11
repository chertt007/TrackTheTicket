# Шаг 3. Subscription Service + Telegram Bot (MVP поток создания подписки)

Документ фиксирует реализацию шага 3 из `implementation-order.md`: полноценный MVP-поток создания подписки через Telegram-диалог и CRUD подписок в отдельном сервисе.

## 1. Цель шага

- Реализовать минимальный рабочий сценарий создания подписки через Telegram.
- Добавить операции управления подпиской: пауза, возобновление, удаление.
- Зафиксировать проверяемые интеграционные тесты.

## 2. Что реализовано

## 2.1 Subscription Service

Добавлены модули:
- [repository.py](C:/Git/TTT/services/subscription-service/src/repository.py)
- [service.py](C:/Git/TTT/services/subscription-service/src/service.py)
- [api.py](C:/Git/TTT/services/subscription-service/src/api.py)
- [main.py](C:/Git/TTT/services/subscription-service/src/main.py)

Функциональность:
- SQLite-хранилище подписок (`SUBSCRIPTION_DB_PATH`, по умолчанию `data/subscriptions.db`).
- CRUD API:
  - `POST /subscriptions`
  - `GET /subscriptions/{id}`
  - `PATCH /subscriptions/{id}` (`action = pause|resume`)
  - `DELETE /subscriptions/{id}`
- Валидация входных данных:
  - `source_url` обязателен;
  - `baggage_mode` обязателен;
  - `reports_per_day >= 1`.

Хранимые поля в MVP:
- `id`
- `chat_id`
- `source_url`
- `baggage_mode`
- `reports_per_day`
- `status` (`active|paused`)
- `created_at`

## 2.2 Telegram Bot Service (диалоговый флоу)

Добавлены модули:
- [subscription_client.py](C:/Git/TTT/apps/telegram-bot/src/subscription_client.py)
- [bot_flow.py](C:/Git/TTT/apps/telegram-bot/src/bot_flow.py)
- [api.py](C:/Git/TTT/apps/telegram-bot/src/api.py)
- [main.py](C:/Git/TTT/apps/telegram-bot/src/main.py)

Реализованный сценарий:
1. Пользователь отправляет `/new`.
2. Бот запрашивает ссылку.
3. Бот запрашивает режим багажа (`cabin_only` или `checked_bag`).
4. Бот запрашивает частоту отчетов (`1..24`).
5. Бот создает подписку через `Subscription Service` и возвращает `subscription_id`.

Команды управления:
- `/pause <subscription_id>`
- `/resume <subscription_id>`
- `/delete <subscription_id>`

Webhook endpoint бота:
- `POST /telegram/update` с payload:
  - `chat_id`
  - `text`

## 3. Тесты

Добавлены тесты:
- [test_subscription_service_crud.py](C:/Git/TTT/tests/test_subscription_service_crud.py)
- [test_telegram_subscription_flow.py](C:/Git/TTT/tests/test_telegram_subscription_flow.py)

Что покрыто:
- создание/чтение/пауза/возобновление/удаление подписки;
- валидация некорректных входных данных;
- end-to-end флоу через Telegram-диалог с реальными HTTP вызовами в Subscription Service;
- команды `/pause`, `/resume`, `/delete`.

Команда запуска:

```bash
python -m unittest discover -s tests -v
```

Фактический результат:
- `Ran 15 tests`
- `OK`

## 4. Соответствие acceptance criteria шага 3

Статус:
- Подписка создается через Telegram без ручного вмешательства: выполнено.
- `reports_per_day`, `baggage_mode`, `source_url` сохраняются корректно: выполнено.
- CRUD подписок покрыт интеграционными тестами: выполнено.

## 5. Ограничения MVP шага 3

- Интеграция с реальным Telegram API пока не подключена (используется webhook-эмуляция через HTTP endpoint).
- Сервис подписок пока хранит MVP-набор полей, без полного flight extraction пайплайна.
- Нет авторизации/подписи webhook (будет добавлено на этапах hardening и production readiness).

## 6. Следующий шаг

Шаг 4: `Flight Extraction Service` с нормализацией параметров рейса и `flight_signature`.
