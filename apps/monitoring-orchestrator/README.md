# monitoring-orchestrator

Orchestrator app that runs the full dual-source check pipeline.
Coordinates extraction, airline discovery, fast check, direct check, and notification.

## Endpoint

- `GET /health`
- `POST /run-check`

## Upstream URLs

Configured by environment variables:

- `FLIGHT_EXTRACTION_URL`
- `AIRLINE_DISCOVERY_URL`
- `FAST_PRICE_PROVIDER_URL`
- `DIRECT_STRATEGY_URL`
- `BROWSER_AUTOMATION_URL`
- `NOTIFICATION_SERVICE_URL`
