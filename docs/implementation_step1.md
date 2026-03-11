# Шаг 1. Foundation монорепозитория

## Цель

Подготовить базовый каркас сервисов и единый HTTP runtime на FastAPI.

## Реализовано

- Общая конфигурация и логирование в `packages/shared`.
- Общий runtime в `packages/shared/runtime/http_service.py`.
- Базовый health endpoint `GET /health` на FastAPI для всех сервисов.
- Единый серверный wrapper поверх uvicorn для запуска/остановки в рантайме и тестах.

## Ключевые решения

1. API-слой стандартизован на FastAPI.
2. Внутренний запуск через uvicorn.
3. Все сервисы могут быть подняты одинаково (`python src/main.py`).

## Проверка

```bash
python -m unittest discover -s tests -v
```

Покрывается:

- корректный `GET /health`;
- корректный scaffold сервисов;
- валидность базовой конфигурации.
