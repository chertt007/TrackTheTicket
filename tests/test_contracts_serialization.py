from datetime import datetime
import unittest

from packages.contracts import (
    CheckResultResponse,
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
    DirectCheckCompletedEvent,
    FastCheckCompletedEvent,
    ReconcileAndNotifyRequestedEvent,
)


class ContractsSerializationTests(unittest.TestCase):
    def test_http_dto_roundtrip(self) -> None:
        req = CreateSubscriptionRequest(
            source_url="https://example.com/flight",
            baggage_mode="checked_bag",
            reports_per_day=2,
        )
        resp = CreateSubscriptionResponse(
            subscription_id="sub-1",
            status="active",
            created_at=datetime(2026, 3, 11, 12, 0, 0),
        )
        result = CheckResultResponse(
            subscription_id="sub-1",
            fast_source_price=150.0,
            direct_price=144.0,
            better_source="direct",
            final_summary="Direct source is cheaper",
            checked_at=datetime(2026, 3, 11, 12, 5, 0),
        )

        self.assertEqual(CreateSubscriptionRequest.from_dict(req.to_dict()), req)
        self.assertEqual(CreateSubscriptionResponse.from_dict(resp.to_dict()), resp)
        self.assertEqual(CheckResultResponse.from_dict(result.to_dict()), result)

    def test_event_roundtrip(self) -> None:
        fast = FastCheckCompletedEvent(
            check_job_id="job-1",
            subscription_id="sub-1",
            fast_source_status="ok",
            fast_source_price=150.0,
            fast_source_currency="EUR",
            occurred_at=datetime(2026, 3, 11, 12, 1, 0),
        )
        direct = DirectCheckCompletedEvent(
            check_job_id="job-1",
            subscription_id="sub-1",
            direct_status="ok",
            direct_price=144.0,
            direct_currency="EUR",
            direct_screenshot_url="https://cdn.local/snap-1.png",
            is_match_confirmed=True,
            occurred_at=datetime(2026, 3, 11, 12, 2, 0),
        )
        reconcile = ReconcileAndNotifyRequestedEvent(
            check_job_id="job-1",
            subscription_id="sub-1",
            triggered_at=datetime(2026, 3, 11, 12, 3, 0),
        )

        self.assertEqual(FastCheckCompletedEvent.from_dict(fast.to_dict()), fast)
        self.assertEqual(DirectCheckCompletedEvent.from_dict(direct.to_dict()), direct)
        self.assertEqual(ReconcileAndNotifyRequestedEvent.from_dict(reconcile.to_dict()), reconcile)


if __name__ == "__main__":
    unittest.main()

