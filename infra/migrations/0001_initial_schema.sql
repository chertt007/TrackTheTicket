PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS subscription (
    id TEXT PRIMARY KEY,
    source_url TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    departure_at TEXT NOT NULL,
    return_at TEXT,
    airline_code TEXT NOT NULL,
    airline_name TEXT NOT NULL,
    airline_domain TEXT NOT NULL,
    flight_number TEXT,
    baggage_mode TEXT NOT NULL,
    reports_per_day INTEGER NOT NULL CHECK (reports_per_day > 0),
    fast_source_type TEXT NOT NULL,
    direct_strategy_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS direct_airline_strategy (
    id TEXT PRIMARY KEY,
    airline_code TEXT NOT NULL,
    airline_domain TEXT NOT NULL,
    strategy_version INTEGER NOT NULL CHECK (strategy_version > 0),
    strategy_json TEXT NOT NULL,
    playwright_script TEXT NOT NULL,
    status TEXT NOT NULL,
    success_rate REAL NOT NULL DEFAULT 0,
    average_runtime_sec REAL NOT NULL DEFAULT 0,
    requires_ai_repair INTEGER NOT NULL DEFAULT 0,
    last_verified_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS check_job (
    id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    fast_check_task_id TEXT NOT NULL,
    direct_airline_check_task_id TEXT NOT NULL,
    reconcile_and_notify_task_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subscription_id) REFERENCES subscription(id)
);

CREATE TABLE IF NOT EXISTS check_result (
    id TEXT PRIMARY KEY,
    check_job_id TEXT NOT NULL,
    fast_source_price REAL,
    fast_source_currency TEXT,
    fast_source_status TEXT NOT NULL,
    direct_price REAL,
    direct_currency TEXT,
    direct_status TEXT NOT NULL,
    direct_screenshot_url TEXT,
    is_match_confirmed INTEGER NOT NULL,
    better_source TEXT,
    final_summary TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    FOREIGN KEY(check_job_id) REFERENCES check_job(id)
);

CREATE INDEX IF NOT EXISTS idx_subscription_airline_code
    ON subscription (airline_code);

CREATE INDEX IF NOT EXISTS idx_subscription_status
    ON subscription (status);

CREATE INDEX IF NOT EXISTS idx_strategy_airline_domain
    ON direct_airline_strategy (airline_domain);

CREATE INDEX IF NOT EXISTS idx_check_job_subscription
    ON check_job (subscription_id);

CREATE INDEX IF NOT EXISTS idx_check_result_job
    ON check_result (check_job_id);

