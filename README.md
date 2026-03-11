# TTT Monorepo

Монорепозиторий для сервиса мониторинга билетов с обязательной двухканальной проверкой цен:

- `Channel A`: быстрый источник (агрегатор/API/кэшированный парсер)
- `Channel B`: прямой сайт авиакомпании

## Структура

См. подробную структуру и назначение папок:

- `docs/architecture/monorepo-structure.md`
- `docs/architecture/implementation-order.md`
- `docs/architecture/system-flow.md` (базовая логика приложения, source of truth)
- `docs/implementation_step1.md` (детальная реализация шага 1 + тесты)
- `docs/implementation_step2.md` (доменные модели, контракты, миграции)
