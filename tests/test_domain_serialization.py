from datetime import datetime
import unittest

from packages.domain import CheckJob, CheckResult, DirectAirlineStrategy, Subscription


class DomainSerializationTests(unittest.TestCase):
    def test_subscription_roundtrip(self) -> None:
        model = Subscription(
            id="sub-1",
            source_url="https://example.com/search",
            origin="TLV",
            destination="BER",
            departure_at=datetime(2026, 5, 10, 9, 30, 0),
            return_at=datetime(2026, 5, 17, 18, 10, 0),
            airline_code="LH",
            airline_name="Lufthansa",
            airline_domain="lufthansa.com",
            flight_number="LH681",
            baggage_mode="cabin_only",
            reports_per_day=3,
            fast_source_type="aggregator_api",
            direct_strategy_id="strat-1",
            status="active",
        )
        self.assertEqual(Subscription.from_dict(model.to_dict()), model)

    def test_strategy_roundtrip(self) -> None:
        model = DirectAirlineStrategy(
            id="strat-1",
            airline_code="LH",
            airline_domain="lufthansa.com",
            strategy_version=2,
            strategy_json='{"steps":[{"type":"navigate"}]}',
            playwright_script="goto-home;search;extract",
            status="operational",
            success_rate=0.97,
            average_runtime_sec=8.4,
            requires_ai_repair=False,
            last_verified_at=datetime(2026, 3, 11, 10, 0, 0),
        )
        self.assertEqual(DirectAirlineStrategy.from_dict(model.to_dict()), model)

    def test_check_job_and_result_roundtrip(self) -> None:
        job = CheckJob(
            id="job-1",
            subscription_id="sub-1",
            fast_check_task_id="task-fast-1",
            direct_airline_check_task_id="task-direct-1",
            reconcile_and_notify_task_id="task-rec-1",
            status="completed",
            created_at=datetime(2026, 3, 11, 11, 0, 0),
        )
        result = CheckResult(
            id="res-1",
            check_job_id="job-1",
            fast_source_price=129.9,
            fast_source_currency="EUR",
            fast_source_status="ok",
            direct_price=124.5,
            direct_currency="EUR",
            direct_status="ok",
            direct_screenshot_url="https://cdn.local/screens/1.png",
            is_match_confirmed=True,
            better_source="direct",
            final_summary="Direct offer is better by 5.4 EUR",
            checked_at=datetime(2026, 3, 11, 11, 5, 0),
        )
        self.assertEqual(CheckJob.from_dict(job.to_dict()), job)
        self.assertEqual(CheckResult.from_dict(result.to_dict()), result)


if __name__ == "__main__":
    unittest.main()

