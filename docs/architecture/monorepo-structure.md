# Monorepo Folder Layout

## Top Level

```text
.
|- apps/
|  |- telegram-bot/
|  |- monitoring-orchestrator/
|  |- ai-strategy-worker/
|  |- browser-automation-worker/
|  `- notification-worker/
|- services/
|  |- subscription-service/
|  |- flight-extraction-service/
|  |- airline-discovery-service/
|  |- fast-price-provider-service/
|  |- direct-airline-strategy-service/
|  |- browser-automation-service/
|  |- ai-strategy-service/
|  `- notification-service/
|- packages/
|  |- domain/
|  |  |- subscription/
|  |  |- direct-airline-strategy/
|  |  |- check-result/
|  |  `- check-job/
|  |- contracts/
|  |  |- http/
|  |  `- events/
|  `- shared/
|     |- config/
|     |- logging/
|     |- errors/
|     `- utils/
|- data/
|  `- airline-strategies/
|     |- manifests/
|     |- playwright/
|     `- snapshots/
|- infra/
|  |- docker/
|  |- k8s/
|  |- terraform/
|  `- monitoring/
`- docs/
   `- architecture/
      `- monorepo-structure.md
```

## Responsibility Split

- `apps/telegram-bot`: прием ссылок, диалог по baggage/частоте, отправка отчетов.
- `apps/monitoring-orchestrator`: запуск цикла `fast_check_task` + `direct_airline_check_task` + `reconcile_and_notify_task`.
- `apps/ai-strategy-worker`: runtime-воркер для discovery/repair задач.
- `apps/browser-automation-worker`: runtime-воркер Playwright задач.
- `apps/notification-worker`: runtime-воркер очереди уведомлений.

- `services/subscription-service`: CRUD подписок и параметры мониторинга.
- `services/flight-extraction-service`: извлечение и нормализация параметров рейса из ссылки.
- `services/airline-discovery-service`: маппинг авиакомпания -> официальный домен/регион.
- `services/fast-price-provider-service`: дешевые быстрые проверки канала A.
- `services/direct-airline-strategy-service`: хранение, версии, статусы и качество стратегий канала B.
- `services/browser-automation-service`: абстракция запуска браузера, шагов стратегии и артефактов.
- `services/ai-strategy-service`: генерация и ремонт стратегий.
- `services/notification-service`: шаблоны и маршрутизация пользовательских/dev уведомлений.

- `packages/domain/*`: доменные сущности (`Subscription`, `DirectAirlineStrategy`, `CheckResult`, `CheckJob`).
- `packages/contracts/*`: межсервисные API-контракты и события.
- `packages/shared/*`: общие модули (конфиг, логи, ошибки, утилиты).

- `data/airline-strategies/manifests`: сериализованные `strategy_json` + мета.
- `data/airline-strategies/playwright`: скрипты/шаги прямого поиска.
- `data/airline-strategies/snapshots`: эталонные HTML/скриншоты для валидации и ремонта.

- `infra/*`: инфраструктура запуска и наблюдаемость.

## Next Build Step

Следующий практичный шаг: в каждом каталоге `apps/*` и `services/*` создать единый базовый каркас (`src`, `tests`, `Dockerfile`, `README`) и зафиксировать контракты `packages/contracts/events` для CheckJob pipeline.
