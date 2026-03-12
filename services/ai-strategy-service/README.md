# ai-strategy-service

Service for repairing direct-airline strategies.
Supports OpenRouter-based generation and deterministic local fallback.

## Endpoints

- `GET /health`
- `GET /ai/provider-config`
- `POST /ai/select-model`
- `POST /strategies/repair`

## OpenRouter setup

Required environment variables for provider mode:

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL_CHEAP` (for simple low-cost tasks)
- `OPENROUTER_MODEL_CODING` (for strategy generation/repair tasks)
- `OPENROUTER_MODEL_ROBUST` (for escalated hard cases)
- `OPENROUTER_BASE_URL` (optional)
- `OPENROUTER_ESCALATE_FAILURE_COUNT` (default `2`)
- `OPENROUTER_ESCALATE_CONFIDENCE_THRESHOLD` (default `0.75`)

Routing strategy:

- simple tasks (`intent_extraction`, `airline_resolution`, `reconcile`, `user_summary`) -> cheap model
- strategy tasks (`strategy_generation`, `strategy_repair`) -> coding model
- escalation (`failure_count >= threshold` or `confidence < threshold`) -> robust model

If `OPENROUTER_API_KEY` is not provided, service uses local fallback strategy generation.
