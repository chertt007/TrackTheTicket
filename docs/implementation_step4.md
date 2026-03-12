# Step 4. Pipeline Services + Monitoring Orchestrator

## Goal

Implement the remaining pipeline services and connect them through a runnable orchestrator flow.

## Implemented

### Pipeline services (FastAPI)

- `flight-extraction-service`
  - `POST /extract-flight`
- `airline-discovery-service`
  - `POST /discover-airline`
- `fast-price-provider-service`
  - `POST /fast-check`
- `direct-airline-strategy-service`
  - `POST /strategies/resolve`
- `browser-automation-service`
  - `POST /direct-check`
- `notification-service`
  - `POST /notifications/send`
- `ai-strategy-service`
  - `GET /ai/provider-config`
  - `POST /ai/select-model`
  - `POST /strategies/repair`

All services keep the unified `GET /health` endpoint.

### Monitoring Orchestrator app

- New app module: `apps/monitoring-orchestrator/src`
- Endpoint: `POST /run-check`
- Coordinates full flow:
  1. extract flight payload,
  2. discover airline,
  3. run fast check,
  4. resolve direct strategy,
  5. run direct check,
  6. reconcile prices,
  7. send notification.

### OpenRouter integration

- AI interactions are implemented via OpenRouter in `ai-strategy-service`.
- Model routing strategy is configurable by env:
  - cheap model for simple tasks,
  - coding model for strategy tasks,
  - robust model for escalated hard cases.
- API key is read from `OPENROUTER_API_KEY`.
- If key is missing or provider fails, service returns a deterministic local fallback strategy.

## Environment variables

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL_CHEAP`
- `OPENROUTER_MODEL_CODING`
- `OPENROUTER_MODEL_ROBUST`
- `OPENROUTER_BASE_URL` (default: `https://openrouter.ai/api/v1`)
- `OPENROUTER_ESCALATE_FAILURE_COUNT` (default: `2`)
- `OPENROUTER_ESCALATE_CONFIDENCE_THRESHOLD` (default: `0.75`)

Orchestrator upstream URLs:

- `FLIGHT_EXTRACTION_URL`
- `AIRLINE_DISCOVERY_URL`
- `FAST_PRICE_PROVIDER_URL`
- `DIRECT_STRATEGY_URL`
- `BROWSER_AUTOMATION_URL`
- `NOTIFICATION_SERVICE_URL`

## Verification

```bash
python -m pytest -q
```

Coverage includes:

- service business logic for step-4 modules,
- OpenRouter client behavior and fallback,
- orchestrator end-to-end composition with mocked upstreams.
