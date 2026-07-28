import unittest
from core.model_router import ModelRouter, ACTION_TIER_MAP


class TestModelRouter(unittest.TestCase):
    def setUp(self):
        self.router = ModelRouter()

    def test_all_18_action_mappings(self):
        for action, expected_tier in ACTION_TIER_MAP.items():
            res = self.router.route(action)
            expected_tier_name = f"T-{expected_tier.capitalize()}"
            self.assertEqual(res["tier"], expected_tier_name)

    def test_unknown_action_defaults_to_mid(self):
        res = self.router.route("UNKNOWN_RANDOM_ACTION")
        self.assertEqual(res["tier"], "T-Mid")
        self.assertEqual(res["model_name"], "gemini-1.5-pro")

    def test_override_tier(self):
        res = self.router.route("ROUTE_TASK", override_tier="high")
        self.assertEqual(res["tier"], "T-High")
        self.assertEqual(res["model_name"], "gemini-1.5-ultra")

    def test_cost_calculation(self):
        res = self.router.route("ROUTE_TASK", input_tokens=1_000_000, output_tokens=1_000_000)
        # Flash rates: $0.075 / 1M in, $0.30 / 1M out -> total 0.375
        self.assertAlmostEqual(res["estimated_cost_usd"], 0.375, places=3)


if __name__ == "__main__":
    unittest.main()
