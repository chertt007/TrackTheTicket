from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SubscriptionRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    chat_id TEXT,
                    source_url TEXT NOT NULL,
                    baggage_mode TEXT NOT NULL,
                    reports_per_day INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def create(self, data: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO subscriptions (
                    id, chat_id, source_url, baggage_mode, reports_per_day, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    data.get("chat_id"),
                    data["source_url"],
                    data["baggage_mode"],
                    data["reports_per_day"],
                    data["status"],
                    data["created_at"],
                ),
            )

    def get(self, subscription_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, chat_id, source_url, baggage_mode, reports_per_day, status, created_at
                FROM subscriptions
                WHERE id = ?
                """,
                (subscription_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "chat_id": row[1],
            "source_url": row[2],
            "baggage_mode": row[3],
            "reports_per_day": int(row[4]),
            "status": row[5],
            "created_at": row[6],
        }

    def update_status(self, subscription_id: str, status: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE subscriptions SET status = ? WHERE id = ?",
                (status, subscription_id),
            )
            return cursor.rowcount > 0

    def delete(self, subscription_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM subscriptions WHERE id = ?", (subscription_id,))
            return cursor.rowcount > 0

