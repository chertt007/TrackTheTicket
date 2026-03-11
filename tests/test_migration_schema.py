from pathlib import Path
import sqlite3
import unittest


ROOT = Path(__file__).resolve().parents[1]
MIGRATION_FILE = ROOT / "infra" / "migrations" / "0001_initial_schema.sql"


class MigrationSchemaTests(unittest.TestCase):
    def test_initial_migration_applies_on_clean_db(self) -> None:
        sql = MIGRATION_FILE.read_text(encoding="utf-8")
        conn = sqlite3.connect(":memory:")
        try:
            conn.executescript(sql)
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
        finally:
            conn.close()

        expected = {
            "subscription",
            "direct_airline_strategy",
            "check_job",
            "check_result",
        }
        self.assertTrue(expected.issubset(tables), msg=f"Missing tables: {expected - tables}")


if __name__ == "__main__":
    unittest.main()

