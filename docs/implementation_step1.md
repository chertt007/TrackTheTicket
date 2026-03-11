# Шаг 1. Foundation монорепозитория: реализация и результаты

Документ фиксирует итог обсуждения и реализации первого этапа из `implementation-order.md`.

## 1. Цель шага

Подготовить технический фундамент, на котором можно безопасно и быстро реализовывать бизнес-логику dual-source мониторинга:
- единый runtime для сервисов;
- единые базовые модули (`config`, `logging`, `errors`);
- одинаковый минимальный каркас для каждого сервиса;
- автопроверка через тесты.

## 2. Принятые решения

1. Базовый язык foundation: `Python 3.10`.
2. На шаге 1 не добавляем внешние зависимости, чтобы получить минимальный, предсказуемый baseline.
3. Для healthcheck используем встроенный `http.server` и единый shared runtime.
4. Все сервисы получают одинаковый минимальный набор файлов:
   - `src/main.py`
   - `tests/`
   - `README.md`
   - `Dockerfile`

## 3. Что реализовано в коде

## 3.1 Общие модули

Добавлены shared-пакеты:
- [settings.py](C:/Git/TTT/packages/shared/config/settings.py)
- [logger.py](C:/Git/TTT/packages/shared/logging/logger.py)
- [app_error.py](C:/Git/TTT/packages/shared/errors/app_error.py)
- [http_service.py](C:/Git/TTT/packages/shared/runtime/http_service.py)

Ключевая функциональность:
- `ServiceSettings.from_env(...)` читает env-переменные и валидирует порт.
- `configure_logging(...)` настраивает единый формат логов.
- `AppError` задает унифицированную модель прикладной ошибки.
- `http_service` создает HTTP-сервер с endpoint `GET /health`.

## 3.2 Каркас сервисов

Для каждого сервиса в `services/*` добавлен entrypoint:
- [main.py](C:/Git/TTT/services/subscription-service/src/main.py)
- [main.py](C:/Git/TTT/services/flight-extraction-service/src/main.py)
- [main.py](C:/Git/TTT/services/airline-discovery-service/src/main.py)
- [main.py](C:/Git/TTT/services/fast-price-provider-service/src/main.py)
- [main.py](C:/Git/TTT/services/direct-airline-strategy-service/src/main.py)
- [main.py](C:/Git/TTT/services/browser-automation-service/src/main.py)
- [main.py](C:/Git/TTT/services/ai-strategy-service/src/main.py)
- [main.py](C:/Git/TTT/services/notification-service/src/main.py)

Каждый `main.py`:
- поднимает shared runtime;
- читает конфиг из env;
- запускает HTTP-сервис с healthcheck.

Также в каждом сервисе добавлены:
- `README.md`
- `Dockerfile`
- папка `tests/`

## 4. Тесты и проверка

Добавлены тесты:
- [test_config.py](C:/Git/TTT/tests/test_config.py)
- [test_health_server.py](C:/Git/TTT/tests/test_health_server.py)
- [test_service_scaffold.py](C:/Git/TTT/tests/test_service_scaffold.py)

Что проверяют:
- корректный парсинг env и валидация порта;
- корректный ответ `GET /health` и структура JSON;
- наличие обязательного foundation-каркаса во всех сервисах.

Команда запуска:

```bash
python -m unittest discover -s tests -v
```

Фактический результат:
- `Ran 5 tests`
- `OK`

## 5. Соответствие acceptance criteria шага 1

Статус по критериям:
- Единый базовый каркас для сервисов: выполнено.
- Базовый health endpoint (`GET /health`): выполнено.
- Базовая тестируемость foundation-слоя: выполнено.

Ограничения текущего шага:
- `docker-compose` оркестрация всех сервисов еще не добавлена;
- CI pipeline пока не настроен.

## 6. Что дальше (шаг 2)

Следующим этапом реализуем доменную модель и контракты:
- `Subscription`, `DirectAirlineStrategy`, `CheckResult`, `CheckJob`;
- контрактные DTO/events;
- стартовые миграции БД.
