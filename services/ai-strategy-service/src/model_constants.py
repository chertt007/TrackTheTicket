"""Model constants grouped by AI task type."""

# Task-specific default models.
INTENT_EXTRACTION_MODEL = "mistralai/mistral-small-3.2-24b-instruct-2506"
AIRLINE_RESOLUTION_MODEL = "mistralai/mistral-small-3.2-24b-instruct-2506"
RECONCILIATION_MODEL = "mistralai/mistral-small-3.2-24b-instruct-2506"
USER_SUMMARY_MODEL = "mistralai/mistral-small-3.2-24b-instruct-2506"
STRATEGY_PLANNING_MODEL = "qwen/qwen3-coder-next"
STRATEGY_REPAIR_MODEL = "qwen/qwen3-coder-next"
ESCALATION_MODEL = "openai/gpt-4o-mini"

# Routing task groups.
SIMPLE_TASK_TYPES = {
    "intent_extraction",
    "airline_resolution",
    "reconcile",
    "user_summary",
}

STRATEGY_TASK_TYPES = {
    "strategy_generation",
    "strategy_repair",
}
