import unittest
from core.cost_tracker import CostTracker


class TestCostTracker(unittest.TestCase):
    def test_record_call_and_summary(self):
        tracker = CostTracker()

        cost1 = tracker.record_call(
            model_name="gemini-2.0-flash-lite",
            tier="T-Low",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            action="ROUTE_TASK",
        )
        self.assertAlmostEqual(cost1, 0.375, places=3)

        summary = tracker.get_summary()
        self.assertEqual(summary["total_calls"], 1)
        self.assertEqual(summary["calls_by_tier"]["low"], 1)
        self.assertFalse(summary["is_over_budget"])

    def test_over_budget_detection(self):
        tracker = CostTracker()
        tracker.monthly_budget = 1.0  # Set low budget for testing

        # Record expensive call
        tracker.record_call(
            model_name="gemini-1.5-pro",
            tier="T-Mid",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            action="ANALYZE_LOSS_TRAJECTORY",
        )
        self.assertTrue(tracker.is_over_budget())


if __name__ == "__main__":
    unittest.main()
