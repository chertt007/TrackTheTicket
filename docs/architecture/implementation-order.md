# Порядок имплементации (Roadmap)

Цель: зафиксировать последовательность разработки dual-source мониторинга, критерии приемки и отдельно выделить контейнеризацию/CI-CD/деплой.

## 1. Базовый foundation монорепозитория

Что делаем:
- фиксируем единый стек;
- создаем шаблон сервиса (`src`, `tests`, `Dockerfile`, `README`, `GET /health`);
- подключаем общий `config/logging/errors`.

Acceptance criteria:
- все сервисы стартуют локально;
- `GET /health` возвращает `200`;
- есть базовый lint/test pipeline.

## 2. Доменная модель и контракты

Что делаем:
- описываем `Subscription`, `DirectAirlineStrategy`, `CheckResult`, `CheckJob`;
- фиксируем HTTP DTO и event-контракты;
- добавляем стартовые миграции.

Acceptance criteria:
- модели и контракты версионированы в `packages/domain` и `packages/contracts`;
- миграции применяются на чистой БД;
- есть тесты сериализации/десериализации DTO и событий.

## 3. Subscription Service + Telegram Bot (MVP создания подписки)

Что делаем:
- сценарий: ссылка, багаж, частота отчетов;
- создание/пауза/возобновление/удаление подписки;
- сохранение состояния процесса создания.

Acceptance criteria:
- подписка создается через Telegram end-to-end;
- `source_url`, `baggage_mode`, `reports_per_day` сохраняются корректно;
- CRUD покрыт интеграционными тестами.

## 4. Flight Extraction Service

Что делаем:
- извлекаем `origin/destination/departure_at/return_at/flight_number`;
- нормализуем формат полей;
- формируем `flight_signature`.

Acceptance criteria:
- точность извлечения на тестовом наборе не ниже 95%;
- неподдерживаемые ссылки дают контролируемую ошибку с reason-code;
- формат данных соответствует доменной схеме.

## 5. Airline Discovery Service

Что делаем:
- определяем авиакомпанию и официальный домен;
- выбираем регион/локаль;
- добавляем кэш и ручной override.

Acceptance criteria:
- для топ-N целевого рынка домен определяется корректно;
- кэш/override покрыты тестами;
- ошибки discovery не ломают подписку, а переводят ее в ожидающий статус.

## 6. Fast Price Provider Service (Канал A)

Что делаем:
- подключаем быстрый источник цены;
- возвращаем `price_fast/currency/source_meta/checked_at`;
- обрабатываем rate-limit и временные ошибки.

Acceptance criteria:
- среднее время fast-check укладывается в SLA;
- временные сбои помечаются как `temporary_failure`;
- результаты сохраняются в истории проверок.

## 7. Direct Airline Strategy Service + lifecycle (Канал B)

Что делаем:
- храним и версионируем стратегии;
- вводим lifecycle `discovery -> operational -> repair`;
- считаем метрики качества стратегий.

Acceptance criteria:
- стратегия для новой авиакомпании создается и активируется;
- версионирование не перезаписывает старые версии;
- есть API выбора активной стратегии по `airline_code/airline_domain`.

## 8. Browser Automation Service

Что делаем:
- исполняем direct-стратегии через Playwright;
- извлекаем direct-price и детали тарифа;
- сохраняем screenshot, HTML snapshot, network logs.

Acceptance criteria:
- сервис стабильно возвращает direct-результат для валидной стратегии;
- `is_match_confirmed` вычисляется детерминированно;
- при падении формируется диагностический артефакт для ремонта.

## 9. Monitoring Orchestrator (dual-source pipeline)

Что делаем:
- в каждом `CheckJob` запускаем `fast_check_task` и `direct_airline_check_task`;
- дожидаемся обоих результатов;
- запускаем `reconcile_and_notify_task`;
- применяем расписание по `reports_per_day`.

Acceptance criteria:
- оба канала обязательны в каждом цикле;
- `CheckResult` хранит поканальные данные;
- отказ одного канала не отменяет второй.

## 10. Reconciliation + Notification Service

Что делаем:
- сравниваем `price_fast` и `price_direct` с учетом baggage/match;
- выбираем `better_source`, формируем `final_summary`;
- отправляем пользователю отчет с двумя ценами и screenshot.

Acceptance criteria:
- формат отчета стабилен и полный;
- поддержаны user/dev каналы уведомлений;
- поведение при частичной деградации формализовано.

## 11. AI Strategy Builder/Repair Service

Что делаем:
- AI только для `discovery` и `repair`;
- анализ неудачных прогонов и выпуск новой версии стратегии.

Acceptance criteria:
- при изменении сайта стратегия ремонтируется и возвращается в `operational`;
- success rate direct-check растет после ремонта;
- стоимость и частота AI вызовов наблюдаемы в метриках.

## 12. Контейнеризация и CI/CD + деплой на Azure (обязательный шаг)

Почему отдельный шаг:
- без него невозможно надежно выпускать изменения и поддерживать сервис в рабочем состоянии.

Целевая low-cost схема:
- `Azure VM (Linux, B1s)` как единый runtime-хост (прод);
- `Azure Container Registry (ACR)` для хранения образов;
- `GitHub Actions` для CI/CD;
- `Docker Compose` на VM для запуска всех контейнеров;
- `Nginx` как reverse proxy + TLS (Let's Encrypt).

Где что разворачиваем:
- На VM (в контейнерах):
  - `telegram-bot`
  - `subscription-service`
  - `flight-extraction-service`
  - `airline-discovery-service`
  - `fast-price-provider-service`
  - `direct-airline-strategy-service`
  - `browser-automation-service`
  - `ai-strategy-service`
  - `monitoring-orchestrator`
  - `notification-service`
  - `postgres` (если небольшая нагрузка, допустимо на том же хосте)
  - `redis`/очередь (если используем)
  - `nginx`
- В ACR:
  - образы всех приложений выше с тегами `:git_sha` и `:latest-main`.
- В GitHub:
  - workflow CI (lint/test/build);
  - workflow CD (push в ACR + деплой на VM по SSH).

Матрица деплоя (пакет -> контейнер -> размещение):

| Пакет/сервис | Имя контейнера | Образ в ACR | Куда деплоим |
|---|---|---|---|
| `apps/telegram-bot` | `telegram-bot` | `tracktheticket/telegram-bot` | Azure VM B1s (docker compose) |
| `services/subscription-service` | `subscription-service` | `tracktheticket/subscription-service` | Azure VM B1s |
| `services/flight-extraction-service` | `flight-extraction-service` | `tracktheticket/flight-extraction-service` | Azure VM B1s |
| `services/airline-discovery-service` | `airline-discovery-service` | `tracktheticket/airline-discovery-service` | Azure VM B1s |
| `services/fast-price-provider-service` | `fast-price-provider-service` | `tracktheticket/fast-price-provider-service` | Azure VM B1s |
| `services/direct-airline-strategy-service` | `direct-airline-strategy-service` | `tracktheticket/direct-airline-strategy-service` | Azure VM B1s |
| `services/browser-automation-service` | `browser-automation-service` | `tracktheticket/browser-automation-service` | Azure VM B1s |
| `services/ai-strategy-service` | `ai-strategy-service` | `tracktheticket/ai-strategy-service` | Azure VM B1s |
| `apps/monitoring-orchestrator` | `monitoring-orchestrator` | `tracktheticket/monitoring-orchestrator` | Azure VM B1s |
| `services/notification-service` + `apps/notification-worker` | `notification-service` | `tracktheticket/notification-service` | Azure VM B1s |
| инфраструктура БД | `postgres` | `postgres:16` | Azure VM B1s (на старте) |
| инфраструктура очереди/кэша | `redis` | `redis:7` | Azure VM B1s (на старте) |
| edge/proxy | `nginx` | `nginx:stable` | Azure VM B1s |

Политика контейнеризации:
- `shared packages` (`packages/*`) не деплоятся как отдельные контейнеры;
- они встраиваются в образы сервисов на этапе сборки.

Минимальный поток CI/CD:
1. Pull Request: lint + unit/integration tests.
2. Merge в `main`: build Docker images для каждого сервиса.
3. Push images в ACR.
4. CD job на VM: `docker compose pull && docker compose up -d`.
5. Smoke-check: health endpoint каждого сервиса.
6. При провале smoke-check: откат на предыдущие теги.

Acceptance criteria:
- у каждого сервиса есть production-ready Dockerfile;
- CI гарантирует зеленые тесты до сборки образов;
- CD автоматически раскатывает изменения на Azure VM;
- после деплоя healthcheck всех контейнеров проходит;
- rollback до предыдущего релиза выполняется одной командой/джобой;
- все секреты хранятся в GitHub Secrets/Azure, не в репозитории.

## 13. Наблюдаемость, надежность, безопасность, production readiness

Что делаем:
- метрики SLA/latency/errors по сервисам и каналам A/B;
- алерты на деградацию direct-check;
- ретраи, дедупликация задач, idempotency, rate limiting;
- аудит логов и безопасное хранение секретов.

Acceptance criteria:
- есть дашборд здоровья dual-source pipeline;
- алерты протестированы и доставляются в нужные каналы;
- проведены нагрузочные и отказоустойчивые проверки.

## Definition of Done для MVP

- пользователь создает подписку через Telegram;
- в каждом цикле мониторинга запускаются оба канала (A и B);
- пользователь получает отчет с двумя ценами, разницей, лучшим источником и screenshot;
- стратегии авиакомпаний версионируются и ремонтируются без остановки системы;
- CI/CD и деплой на Azure VM работают автоматически.
